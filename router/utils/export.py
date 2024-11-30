import pandas as pd
from io import StringIO, BytesIO
from fastapi.responses import JSONResponse, FileResponse
from fpdf import FPDF
from fastapi.responses import FileResponse

def export_transactions_to_json(data):
    """
    Экспортирует данные в формате JSON.

    :param data: Данные для экспорта.
    :return: JSONResponse с переданными данными.
    """
    return JSONResponse(content=data)

def export_transactions_to_csv(dataframes: dict, filename):
    """
    Экспортирует данные в формате CSV.

    :param dataframes: Словарь с названиями и соответствующими DataFrame.
    :return: FileResponse с файлом CSV.
    """
    buffer = StringIO()
    for name, df in dataframes.items():
        df.to_csv(buffer, index=False)
        buffer.write("\n")  # Разделяем таблицы новой строкой
    buffer.seek(0)
    return FileResponse(
        buffer, 
        media_type="text/csv", 
        filename=f"{filename}.csv"
    )


def export_transactions_to_excel(dataframes: dict, filename: str):
    """
    Экспортирует транзакции в формате Excel.
    
    :param dataframes: Словарь с данными для каждой цели или кредита.
    :param filename: Название файла.
    :return: FileResponse с файлом Excel.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, df in dataframes.items():
            df.to_excel(writer, index=False, sheet_name=name)
    buffer.seek(0)
    return FileResponse(
        buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        filename=f"{filename}.xlsx"
    )


def export_transactions_to_pdf(data: list, filename: str):
    """
    Экспортирует транзакции в формате PDF.
    
    :param data: Данные транзакций для отображения в PDF.
    :param filename: Название файла.
    :return: FileResponse с файлом PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Transaction Report", ln=True, align="C")
    
    for item in data:
        pdf.ln(10)
        for key, value in item.items():
            pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return FileResponse(
        buffer,
        media_type="application/pdf",
        filename=f"{filename}.pdf"
    )