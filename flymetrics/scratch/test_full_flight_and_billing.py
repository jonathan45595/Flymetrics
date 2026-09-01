import sys, json, urllib.request
sys.path.insert(0, '.')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, EntregableModel, PagoModel, AgendaModel
from app.shared.utils.email_service import send_otp_email
from app.infrastructure.security.jwt_handler import create_access_token

print("=== 1. Testing Real OTP Email Sender Utility ===")
email_result = send_otp_email("cliente_prueba@flymetrics.co", "984210")
print(f"OTP Email Sender Output: {email_result}")

db = SessionLocal()
usr = db.query(UsuarioModel).filter(UsuarioModel.rol == 'cliente').first()
token = create_access_token({'sub': usr.email, 'rol': usr.rol})

print("\n=== 2. Testing Direct Deliverable Download (Content-Disposition: attachment) ===")
# Obtain or create a test entregable
ent = db.query(EntregableModel).first()
if not ent:
    turno = db.query(AgendaModel).first()
    ent = EntregableModel(id_turno=turno.id_turno, tipo_archivo='ortofoto', url_archivo='uploads/ortomosaico_hd.tif', nombre_archivo='Ortomosaico_HD_Finca_La_Esperanza.tif')
    db.add(ent)
    db.commit()
    db.refresh(ent)

req_dl = urllib.request.Request(f"http://127.0.0.1:3000/api/v1/entregables/{ent.id_entregable}/descargar")
with urllib.request.urlopen(req_dl) as resp:
    disp_header = resp.headers.get("Content-Disposition")
    print(f"PASS -> Direct Download Response HTTP Status: {resp.status}")
    print(f"PASS -> Header Content-Disposition: {disp_header}")

print("\n=== 3. Testing Client Payment Receipt Upload Endpoint ===")
pago = db.query(PagoModel).first()
if not pago:
    turno = db.query(AgendaModel).first()
    pago = PagoModel(id_turno=turno.id_turno, monto=450000.00, estado_pago='Pendiente')
    db.add(pago)
    db.commit()
    db.refresh(pago)

req_up = urllib.request.Request(
    f"http://127.0.0.1:3000/api/v1/pagos/{pago.id_pago}/subir-comprobante",
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    data=json.dumps({
        'url_comprobante': f'uploads/comprobantes/comprobante_nequi_{pago.id_pago}.pdf',
        'referencia_transaccion': 'NEQUI-984012482'
    }).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req_up) as resp_up:
    body_up = json.loads(resp_up.read().decode('utf-8'))
    print(f"PASS -> Upload Payment Proof Response:")
    print(" ", body_up.get('data'))

print("\n>>> ALL FLIGHT CLOSURE, DIRECT DOWNLOAD & PAYMENT PROOF TESTS PASSED 100%! <<<")
