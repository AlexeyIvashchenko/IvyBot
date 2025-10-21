# config.py
import os

# Токен бота от BotFather
BOT_TOKEN = "8383122268:AAH-YqfwGBdkrAyeRTAerusaf3sJI7aTJd4"

# Ваш ID в Telegram (можно узнать у @userinfobot)
ADMIN_ID = 1049262607  # замените на ваш ID

# Настройки ЮKassa
YKASSA_SHOP_ID = "1189684"
YKASSA_SECRET_KEY = "test_DLJOgncejANZ4ur9bX_QguVoeP3QbNNrZhxqXeF8J-A"

# Google Sheets
SPREADSHEET_ID = "1yxsqY7W73TX2rpruVBOLtD72HyvH9CggXYBmlQQgdC4"  # из URL таблицы

# Данные для Google Sheets API (из скачанного JSON файла)
GOOGLE_SHEETS_CREDENTIALS = {
    "type": "service_account",
    "project_id": "ivybo-475514",
    "private_key_id": "7604a603349894539b65eb2f27505b464b83b8e2",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC2+CmaRMiTpsj5\nBX0HtvUNVjwfa5WK+UjEADvssoFMxPlp/C+yZbEHwKtrexGYVPeS1EERdHZ40DXI\nSbFShVUjoCPKfJrX5iw+YztkCvxj82sCPanjxfIz06Ku8ci7yLv3W053+rpruXVx\nNNmLiw7EussrhXEB/ss2wWncLyrialFQ9oRGWhtkim+YAWMQAI7c+jOx0YOEXCDe\n+7L8TR0nhe1xvPnr+yMr0js5kl9MIkwGwtXcO3Ew7toGJMrtWOJK9oXmlxZlv5He\n13S05S57iYhwIdJSuYdQ/I5pI3Z5fdoByvGHhtMUgP4/V7W4enw7fy6eYaFEq2t9\nT6cHOQRNAgMBAAECggEABLeCDw2N5CyNCspm7j97ssPR2feCi+ogQ5lD8jap2apM\nSbysGBvCBBKl+KfcDMLH/RuGr+YCNdwcPtUTgq6YQspakdpDfaRb6KHTQqF73zHD\nxPOFAS+1rjta+sqV461plxdd/v7SNnu5+NilcRD9KPotyanvf18rqvYyffAjWWHc\nFB71ULL0uMAnbdLYw6XzoTyMowGqD2yUddoHqTggLb4hefKiEydWgIE8opDxgQOW\nlPZxcKtSfmoQC3zov7N9EGGSQQIFqmdrjp35Y6EO0FeHSel1NhifF/zu/A/iI436\nQo65m0DSjJ245AHUFpsy1X8tgSbz3MuNPqj/3c17WwKBgQDqUvkDw9wyevlVAjja\nTIFe1xSCRJ1eXnjCdIipflCNGwky2al8Yoyx6cSQj5TuLR50aXlfPc8hN4wR3YQR\nPNz61Ilz9Pva5m6Rarw6PjCJ/KrhH561wtt1q6ytIP966xW7QwrU20rABmbDNdEv\nye+QhbmnVPg9fh+hh9qBWLkqNwKBgQDH5Q8WpXPr1faZCQ0pTeGi2YyduFBk7R8C\n1HEkH2RfRyfq/n1m/fd47w7IKlGtvLzWspKDQQtjVVo6GOBUYPlADFazJ0ej/AH8\n4xfRcRt112I7g507Ff3cN4dXjAsaLG3BLHTHmGVRpNPsIlecq5nuQaBnpNzst0FP\nCmgcsiizmwKBgQCsql9b6uNDP2KixXRnR6C85ffy1eSwOST7BSv+2Vk54QYyNjmx\nslzCbOOvMl4n849RcLdC+yS58ViBgZ1jplmfayWuEIPVlZ88AE6bDGBwDYNNSCOH\nBAL6/nnLSVl4len5hzlgCAdY4F6w0eNHN6IT+LYJG4+goGNmf9j/HwWymQKBgQCt\nT17unpLL9Z2xf5SGrDymSgJNuMETUDdj57cUv5bxuKrWZsFpK2aF1pa1W2Onw4zi\nhL7cx+dMv3LUDj9pSQ6xxkDhYXwOpG9Ax9AdyfgqCozj1q/ay61nYkmY0RXLIpwi\nMR4q82ldCRComfnmHy390a52Tg0xu40HL5mmz5zUYwKBgQDW+UOBr3ggwinP7ClM\nljmPV9nMaO+wXzYQjb30xr9PazUifcv9E6bA9Di6oGCrRlnqKrxboS1zt7U2zRyM\nv2IdlX7vcTFfafH3h5nfgNywA3I/ipLhu6vfvpurhVGzLykCa9jrw05DOX1AhPP0\nXQ2L5rXWesy/raswkDrvYloh2Q==\n-----END PRIVATE KEY-----\n",
    "client_email": "ivy-bot-service@ivybo-475514.iam.gserviceaccount.com",
    "client_id": "109077695381780273576",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
}

# Цены
DEPOSIT_AMOUNT = 4000.00
FINAL_AMOUNT = 11000.00
TOTAL_AMOUNT = 15000.00

# Ссылки
BRIEF_FORM_URL = "https://forms.gle/ВАША_ФОРМА"  # ваша Google форма

# Примеры работ
EXAMPLES = {
    "sites": [
        "https://example-site1.com",
        "https://example-site2.com",
        "https://example-site3.com"
    ],
    "ads": [
        "ads/photo1.jpg",
        "ads/photo2.jpg",
        "ads/photo3.jpg"
    ]
}

# Настройки напоминаний
REMINDER_HOUR = 12  # время отправки напоминаний (9 утра)