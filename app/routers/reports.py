import csv, io
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse

from app.auth import get_current_user
from app.database import run_query
from app.reports_config import REPORTS
from app.templates import render

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    return render("dashboard.html", {"user": user, "reports": REPORTS})


@router.get("/report/{report_id}", response_class=HTMLResponse)
async def view_report(request: Request, report_id: str, user: dict = Depends(get_current_user)):
    cfg = REPORTS.get(report_id)
    if not cfg:
        return HTMLResponse("Relatório não encontrado", status_code=404)

    rows, columns, error, param_value = [], [], None, None

    query_param_key = cfg.get("query_param")
    if query_param_key:
        param_value = request.query_params.get(query_param_key)
        if param_value:
            try:
                rows, columns = await run_query(cfg["sql"], (param_value,))
            except Exception as e:
                error = str(e)
    else:
        try:
            rows, columns = await run_query(cfg["sql"], tuple(cfg.get("params", [])))
        except Exception as e:
            error = str(e)

    return render("report.html", {
        "user": user, "report_id": report_id, "cfg": cfg,
        "columns": columns, "rows": rows, "error": error,
        "param_value": param_value, "reports": REPORTS,
    })


@router.get("/report/{report_id}/download")
async def download_report(request: Request, report_id: str, user: dict = Depends(get_current_user)):
    cfg = REPORTS.get(report_id)
    if not cfg:
        return HTMLResponse("Relatório não encontrado", status_code=404)

    query_param_key = cfg.get("query_param")
    params: tuple = ()
    if query_param_key:
        pv = request.query_params.get(query_param_key, "")
        params = (pv,) if pv else ()

    rows, columns = await run_query(cfg["sql"], params)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{report_id}.csv"'},
    )
