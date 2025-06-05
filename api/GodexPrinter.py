import serial
import serial.tools.list_ports
import win32print
import win32api
import time
import logging
from typing import Optional, List, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GodexPrinterManager:
    def __init__(self):
        self.serial_connection = None
        self.printer_port = None
        self.printer_name = None

    def find_godex_printers(self) -> Dict:
        """Busca impresoras Godex disponibles por puerto serial y drivers de Windows"""
        found_printers = {
            'serial_ports': [],
            'windows_printers': [],
            'usb_printers': []
        }

        # Buscar por puertos seriales
        logger.info("Buscando impresoras por puertos seriales...")
        ports = serial.tools.list_ports.comports()

        for port in ports:
            logger.info(f"Puerto encontrado: {port.device} - {port.description}")
            # Godex suele aparecer con estas descripciones
            if any(keyword in port.description.lower() for keyword in 
                   ['godex', 'usb serial', 'usb-serial', 'prolific', 'ftdi']):
                found_printers['serial_ports'].append({
                    'port': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                })

        # Buscar por drivers de Windows
        logger.info("Buscando impresoras por drivers de Windows...")
        try:
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )
            for printer in printers:
                printer_name = printer[2]
                logger.info(f"Impresora Windows encontrada: {printer_name}")

                # Buscar impresoras Godex, BP500, o con puerto USB
                if any(keyword in printer_name.lower() for keyword in 
                       ['godex', 'bp500', 'bp-500']):
                    try:
                        hprinter = win32print.OpenPrinter(printer_name)
                        printer_info = win32print.GetPrinter(hprinter, 2)
                        win32print.ClosePrinter(hprinter)
                        port_name = printer_info.get('pPortName', 'Unknown')

                        found_printers['windows_printers'].append({
                            'name': printer_name,
                            'port': port_name,
                            'status': printer[0],
                            'driver': printer_info.get('pDriverName', 'Unknown')
                        })

                        # Si es puerto USB, agregarlo también a la lista USB
                        if 'usb' in port_name.lower():
                            found_printers['usb_printers'].append({
                                'name': printer_name,
                                'port': port_name,
                                'driver': printer_info.get('pDriverName', 'Unknown')
                            })
                    except Exception as e:
                        logger.warning(f"Error obteniendo info de {printer_name}: {e}")
                        found_printers['windows_printers'].append({
                            'name': printer_name,
                            'port': 'Unknown',
                            'status': printer[0],
                            'driver': 'Unknown'
                        })
        except Exception as e:
            logger.warning(f"Error buscando impresoras Windows: {e}")

        return found_printers

    def test_serial_connection(self, port: str, baudrate: int = 9600) -> bool:
        """Prueba la conexión serial con la impresora"""
        try:
            test_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )

            # Enviar comando de status EPL
            test_connection.write(b'\x02')  # STX - comando de status
            time.sleep(0.5)

            # Leer respuesta
            response = test_connection.read(100)
            test_connection.close()

            if response:
                logger.info(f"Respuesta de {port}: {response.hex()}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error probando puerto {port}: {e}")
            return False

    def connect_serial(self, port: str = None, baudrate: int = 9600) -> bool:
        """Conecta por puerto serial"""
        if port is None:
            # Auto-detectar puerto
            printers = self.find_godex_printers()
            for printer_info in printers['serial_ports']:
                if self.test_serial_connection(printer_info['port'], baudrate):
                    port = printer_info['port']
                    break

            if port is None:
                logger.error("No se pudo detectar automáticamente la impresora por serial")
                return False

        try:
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=5,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.printer_port = port
            logger.info(f"Conectado exitosamente al puerto serial {port}")
            return True

        except Exception as e:
            logger.error(f"Error conectando al puerto {port}: {e}")
            return False

    def connect_windows_printer(self, printer_name: str = None) -> bool:
        """Conecta usando el driver de Windows (para puertos USB)"""
        if printer_name is None:
            # Auto-detectar impresora
            printers = self.find_godex_printers()
            if printers['windows_printers']:
                printer_name = printers['windows_printers'][0]['name']
            elif printers['usb_printers']:
                printer_name = printers['usb_printers'][0]['name']
            else:
                logger.error("No se encontró impresora Windows")
                return False

        try:
            # Verificar que la impresora existe
            win32print.OpenPrinter(printer_name)
            self.printer_name = printer_name
            logger.info(f"Conectado exitosamente a la impresora Windows: {printer_name}")
            return True

        except Exception as e:
            logger.error(f"Error conectando a impresora Windows {printer_name}: {e}")
            return False

    def get_windows_printer_status(self) -> str:
        """Obtiene el estado de la impresora Windows conectada"""
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            win32print.ClosePrinter(hprinter)

            status_flags = printer_info['Status']
            if status_flags == 0:
                return "✅ Impresora lista"
            else:
                status_messages = []
                if status_flags & win32print.PRINTER_STATUS_PAUSED:
                    status_messages.append("Pausada")
                if status_flags & win32print.PRINTER_STATUS_ERROR:
                    status_messages.append("Error genérico")
                if status_flags & win32print.PRINTER_STATUS_PENDING_DELETION:
                    status_messages.append("Eliminando")
                if status_flags & win32print.PRINTER_STATUS_PAPER_JAM:
                    status_messages.append("Atasco papel")
                if status_flags & win32print.PRINTER_STATUS_PAPER_OUT:
                    status_messages.append("Sin papel")
                if status_flags & win32print.PRINTER_STATUS_OFFLINE:
                    status_messages.append("Offline")
                return f"⚠️ Estado actual: {', '.join(status_messages)}"
        except Exception as e:
            return f"❌ Error obteniendo estado: {e}"

    def check_last_job(self) -> None:
        """Revisa el estado del último trabajo en cola para la impresora Windows"""
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            # Enumera hasta 10 trabajos (nivel 1: JOB_INFO_1)
            jobs = win32print.EnumJobs(hprinter, 0, 10, 1)
            win32print.ClosePrinter(hprinter)

            if not jobs:
                logger.info("No hay trabajos en la cola.")
                return

            ultimo = jobs[-1]
            estado = ultimo['Status']
            nombre = ultimo['pDocument']

            if estado == 0:
                logger.info(f"El trabajo '{nombre}' se imprimió sin errores.")
            else:
                detalles = []
                if estado & win32print.JOB_STATUS_BLOCKED:
                    detalles.append("Bloqueado")
                if estado & win32print.JOB_STATUS_ERROR:
                    detalles.append("Error en trabajo")
                if estado & win32print.JOB_STATUS_PAPEROUT:
                    detalles.append("Sin papel")
                if estado & win32print.JOB_STATUS_OFFLINE:
                    detalles.append("Impresora offline")
                logger.warning(f"Trabajo '{nombre}' terminó con estado: {', '.join(detalles)}")
        except Exception as e:
            logger.error(f"❌ Error consultando trabajos: {e}")

    def send_epl_to_windows_printer(self, epl_command: str) -> bool:
        """Envía comando EPL usando el driver de Windows y luego verifica estado"""
        if not self.printer_name:
            logger.error("No hay impresora Windows conectada")
            return False

        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                # Crear trabajo de impresión
                job_info = ("Etiqueta EPL", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                win32print.StartPagePrinter(hprinter)

                # Enviar datos EPL en formato RAW
                epl_bytes = epl_command.encode('ascii')
                win32print.WritePrinter(hprinter, epl_bytes)

                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)

                logger.info(f"Comando EPL enviado exitosamente (Job ID: {job_id})")

                # Esperar un momento para que el trabajo llegue a la impresora física
                time.sleep(0.5)

                # Obtener estado desde el driver Windows
                status_windows = self.get_windows_printer_status()
                logger.info(f"Estado tras impresión (Windows): {status_windows}")

                # Revisar el último trabajo en cola
                self.check_last_job()

                return True

            finally:
                win32print.ClosePrinter(hprinter)

        except Exception as e:
            logger.error(f"Error enviando EPL a impresora Windows: {e}")
            return False

    def send_epl_command(self, epl_command: str) -> bool:
        """Envía comando EPL a la impresora (serial o Windows) y obtiene status"""
        # Intentar primero por Windows si hay impresora conectada
        if self.printer_name:
            return self.send_epl_to_windows_printer(epl_command)

        # Si no, intentar por serial
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("No hay conexión serial activa")
            return False

        try:
            # Asegurar que el comando termine con \n
            if not epl_command.endswith('\n'):
                epl_command += '\n'

            logger.info(f"Enviando comando EPL por serial:\n{epl_command}")
            self.serial_connection.write(epl_command.encode('ascii'))
            self.serial_connection.flush()

            # Esperar a que la impresora procese el comando
            time.sleep(0.5)

            # Solicitar estado por serial (STX = 0x02)
            self.serial_connection.write(b'\x02')
            time.sleep(0.5)
            status_bytes = self.serial_connection.read(32)  # lee hasta 32 bytes de respuesta

            if status_bytes:
                hexstr = status_bytes.hex()
                logger.info(f"Respuesta de status por serial (hex): {hexstr}")
                # Aquí podrías interpretar los bits según el manual de Godex EPL
            else:
                logger.warning("No se recibió respuesta de status por serial")

            return True

        except Exception as e:
            logger.error(f"Error enviando comando EPL por serial: {e}")
            return False

    def print_sample_ticket(self) -> bool:
        """Imprime un ticket de prueba - Tamaño 57x70mm"""
        # Configuración para 57mm x 70mm (aproximadamente 456 x 560 dots a 203 DPI)
        epl_command = """
N
q456
Q560,24
B30,40,0,1,2,3,80,B,"123456789012"
A30,130,0,2,1,1,N,"PRODUCTO EJEMPLO"
A30,160,0,1,1,1,N,"Precio: $99.99"
A30,185,0,1,1,1,N,"Fecha: 04/06/2025"
A30,210,0,1,1,1,N,"SKU: DEMO001"
P1,1
"""
        return self.send_epl_command(epl_command)

    def print_custom_ticket(self, product_data: Dict) -> bool:
        """Imprime ticket personalizado con datos del producto - Tamaño 57x70mm"""
        # Configuración para 57mm x 70mm (aproximadamente 456 x 560 dots a 203 DPI)
        epl_command = f"""
N
q456
Q560,24
B30,40,0,1,2,3,80,B,"{product_data.get('barcode', '000000000000')}"
A30,130,0,2,1,1,N,"{product_data.get('name', 'PRODUCTO')[:20]}"
A30,160,0,1,1,1,N,"Precio: ${product_data.get('price', '0.00')}"
A30,185,0,1,1,1,N,"SKU: {product_data.get('sku', 'N/A')}"
A30,210,0,1,1,1,N,"Fecha: {product_data.get('date', time.strftime('%d/%m/%Y'))}"
P1,1
"""
        return self.send_epl_command(epl_command)

    def get_printer_status(self) -> str:
        """Obtiene el estado de la impresora (serial o Windows)"""
        if self.printer_name:
            # Para impresoras Windows
            return self.get_windows_printer_status()

        elif self.serial_connection and self.serial_connection.is_open:
            try:
                # Enviar comando de status EPL
                self.serial_connection.write(b'\x02')
                time.sleep(0.5)
                response = self.serial_connection.read(100)
                return f"Status response: {response.hex()}" if response else "Sin respuesta"
            except Exception as e:
                return f"Error: {e}"
        else:
            return "❌ No conectado"

    def disconnect(self):
        """Cierra la conexión"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Conexión serial cerrada")

        if self.printer_name:
            logger.info(f"Desconectado de impresora Windows: {self.printer_name}")
            self.printer_name = None

    def create_57x70_ticket_layout(self, product_data: Dict, layout_style: str = "standard") -> str:
        """
        Crea diferentes layouts de ticket para papel 57x70mm
        
        Args:
            product_data: Diccionario con datos del producto
            layout_style: 'standard', 'compact', 'barcode_top', 'minimal'
        
        Returns:
            Comando EPL formateado
        """
        width_dots = 456
        height_dots = 560
        gap_dots = 24

        name = product_data.get('name', 'PRODUCTO')[:18]
        price = product_data.get('price', '0.00')
        barcode = product_data.get('barcode', '000000000000')
        sku = product_data.get('sku', 'N/A')
        date = product_data.get('date', time.strftime('%d/%m/%Y'))

        if layout_style == "standard":
            return f"""
N
q{width_dots}
Q{height_dots},{gap_dots}
A30,20,0,2,1,1,N,"{name}"
A30,50,0,1,1,1,N,"Precio: ${price}"
B30,80,0,1,2,3,80,B,"{barcode}"
A30,170,0,1,1,1,N,"SKU: {sku}"
A30,195,0,1,1,1,N,"{date}"
P1,1
"""

        elif layout_style == "compact":
            return f"""
N
q{width_dots}
Q{height_dots},{gap_dots}
A25,15,0,1,1,1,N,"{name}"
A25,35,0,1,1,1,N,"${price}"
B25,55,0,1,1,2,60,B,"{barcode}"
A25,125,0,1,1,1,N,"{sku} - {date}"
P1,1
"""

        elif layout_style == "barcode_top":
            return f"""
N
q{width_dots}
Q{height_dots},{gap_dots}
B30,20,0,1,2,3,80,B,"{barcode}"
A30,110,0,2,1,1,N,"{name}"
A30,140,0,1,1,1,N,"Precio: ${price}"
A30,165,0,1,1,1,N,"SKU: {sku}"
A30,190,0,1,1,1,N,"{date}"
P1,1
"""

        elif layout_style == "minimal":
            return f"""
N
q{width_dots}
Q{height_dots},{gap_dots}
A30,30,0,2,1,1,N,"{name}"
A30,60,0,2,1,1,N,"${price}"
B30,90,0,1,2,2,70,B,"{barcode}"
P1,1
"""

        else:
            return self.create_57x70_ticket_layout(product_data, "standard")

    def print_57x70_ticket(self, product_data: Dict, layout_style: str = "standard") -> bool:
        """Imprime ticket con layout específico para 57x70mm"""
        epl_command = self.create_57x70_ticket_layout(product_data, layout_style)
        return self.send_epl_command(epl_command)


# Función principal de ejemplo
def main():
    printer = GodexPrinterManager()

    # Buscar impresoras disponibles
    print("Buscando impresoras Godex...")
    available_printers = printer.find_godex_printers()

    print("\n=== IMPRESORAS ENCONTRADAS ===")
    print("Puertos seriales:")
    for printer_info in available_printers['serial_ports']:
        print(f"  - {printer_info['port']}: {printer_info['description']}")

    print("Impresoras Windows:")
    for printer_info in available_printers['windows_printers']:
        print(f"  - {printer_info['name']} (Puerto: {printer_info['port']})")

    print("Impresoras USB:")
    for printer_info in available_printers['usb_printers']:
        print(f"  - {printer_info['name']} (Puerto: {printer_info['port']})")

    # Intentar conectar - priorizar Windows/USB
    print("\nIntentando conectar...")
    connected = False

    # Primero intentar por Windows (USB)
    if available_printers['usb_printers'] or available_printers['windows_printers']:
        if printer.connect_windows_printer():
            print(f"✅ Conectado exitosamente a impresora Windows: {printer.printer_name}")
            connected = True

    # Si no funciona, intentar por serial
    if not connected and printer.connect_serial():
        print(f"✅ Conectado exitosamente al puerto serial: {printer.printer_port}")
        connected = True

    if connected:
        # Obtener status
        status = printer.get_printer_status()
        print(f"Status de impresora: {status}")

        # Imprimir ticket de prueba
        print("\n¿Desea imprimir un ticket de prueba? (s/n): ", end="")
        if input().lower() == 's':
            if printer.print_sample_ticket():
                print("✅ Ticket enviado correctamente")
            else:
                print("❌ Error enviando ticket")

        # Ejemplo con datos personalizados para 57x70mm
        product_data = {
            'name': 'PRODUCTO DEMO',
            'price': '25.50',
            'barcode': '7501234567890',
            'sku': 'DEMO001',
            'date': time.strftime('%d/%m/%Y')
        }

        print("\n¿Desea imprimir ticket personalizado 57x70mm? (s/n): ", end="")
        if input().lower() == 's':
            print("Seleccione el estilo de layout:")
            print("1. Standard (texto arriba, código abajo)")
            print("2. Compact (todo compacto)")
            print("3. Barcode Top (código arriba)")
            print("4. Minimal (solo esencial)")

            layout_choice = input("Opción (1-4): ").strip()
            layout_styles = {
                '1': 'standard',
                '2': 'compact',
                '3': 'barcode_top',
                '4': 'minimal'
            }

            layout_style = layout_styles.get(layout_choice, 'standard')

            if printer.print_57x70_ticket(product_data, layout_style):
                print(f"✅ Ticket 57x70mm ({layout_style}) enviado correctamente")
            else:
                print("❌ Error enviando ticket 57x70mm")

        printer.disconnect()
    else:
        print("❌ No se pudo conectar a la impresora")
        print("\nDetalles encontrados:")
        if available_printers['windows_printers']:
            print("Impresoras Windows disponibles:")
            for p in available_printers['windows_printers']:
                print(f"  - {p['name']} en puerto {p['port']}")
        if available_printers['serial_ports']:
            print("Puertos seriales disponibles:")
            for p in available_printers['serial_ports']:
                print(f"  - {p['port']}: {p['description']}")
        else:
            print("Puertos disponibles para prueba manual:")
            ports = serial.tools.list_ports.comports()
            for port in ports:
                print(f"  - {port.device}: {port.description}")

if __name__ == "__main__":
    main()
