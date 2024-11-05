import socket
import requests
from colorama import Fore, Style, init
import readline

# Inicializar colorama para colores en la terminal
init(autoreset=True)

# Banner del script
BANNER = f"""
{Fore.CYAN}

██████╗ ███████╗██╗   ██╗███████╗██████╗ ███████╗███████╗    ██╗██████╗ 
██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝    ██║██╔══██╗
██████╔╝█████╗  ██║   ██║█████╗  ██████╔╝███████╗█████╗      ██║██████╔╝
██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══╝      ██║██╔═══╝ 
██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████║███████╗    ██║██║     
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝     
             	Idea de MrVip by SunplaceSolutions                     

{Style.RESET_ALL}
"""

# Módulo para resolver IP de un dominio
def get_ip_from_domain(domain):
    """Resuelve la IP de un dominio."""
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"{Fore.YELLOW}Dirección IP obtenida para {domain}: {ip_address}{Style.RESET_ALL}")
        return ip_address
    except socket.gaierror:
        print(f"{Fore.RED}No se pudo resolver la IP del dominio.{Style.RESET_ALL}")
        return None

# Módulo de búsqueda con YouGetSignal
def get_domains_from_yougetsignal(ip_address):
    """Consulta el servicio de YouGetSignal para obtener dominios en la misma IP."""
    url = 'https://domains.yougetsignal.com/domains.php'
    data = {
        'remoteAddress': ip_address,
        'key': ''  # Este campo se deja vacío
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "Success":
                domains = [item[0] for item in response_data.get("domainArray", [])]
                print(f"{Fore.GREEN}{len(domains)} dominios encontrados a través de YouGetSignal.{Style.RESET_ALL}")
                return domains
            else:
                print(f"{Fore.RED}Error en la respuesta de YouGetSignal: {response_data.get('message')}{Style.RESET_ALL}")
                return []
        else:
            print(f"{Fore.RED}Error en la API de YouGetSignal: {response.status_code}{Style.RESET_ALL}")
            return []
    except Exception as e:
        print(f"{Fore.RED}Error al conectarse a YouGetSignal: {e}{Style.RESET_ALL}")
        return []

# Módulo para obtener el estado HTTP y tipo de CMS
def get_http_status_and_cms(domain):
    """Obtiene el código de estado HTTP y detecta el CMS o tecnología del sitio."""
    url = f"http://{domain}"  # Intentar con http, podría adaptarse a https si es necesario
    try:
        response = requests.head(url, timeout=5)  # Solicitud HEAD para obtener solo el encabezado
        status_code = response.status_code

        # Detección básica de CMS por encabezados o contenido
        cms = "Desconocido"
        server = response.headers.get("Server", "").lower()
        x_powered_by = response.headers.get("X-Powered-By", "").lower()
        
        if "wordpress" in server or "wordpress" in x_powered_by:
            cms = "WordPress"
        elif "drupal" in server or "drupal" in x_powered_by:
            cms = "Drupal"
        elif "joomla" in server or "joomla" in x_powered_by:
            cms = "Joomla"
        elif "wix" in server:
            cms = "Wix"
        elif "shopify" in server:
            cms = "Shopify"
        elif "squarespace" in server:
            cms = "Squarespace"
        elif "cloudflare" in server:
            cms = "Cloudflare"
        
        return status_code, cms
    except requests.RequestException:
        return "Error", "No accesible"

# Función principal para realizar el Reverse IP Domain Check
def reverse_ip_domain_check(domain_or_ip):
    """Realiza el Reverse IP Domain Check usando YouGetSignal y verifica estado HTTP y CMS."""
    
    # Determinar si el input es un dominio o una IP
    if domain_or_ip.replace('.', '').isdigit():
        ip_address = domain_or_ip
    else:
        ip_address = get_ip_from_domain(domain_or_ip)
    
    if not ip_address:
        print(f"{Fore.RED}No se pudo obtener una dirección IP válida.{Style.RESET_ALL}")
        return []
    
    # Intentar con YouGetSignal
    print(f"{Fore.CYAN}Consultando YouGetSignal para obtener dominios en la misma IP...{Style.RESET_ALL}")
    domains = get_domains_from_yougetsignal(ip_address)
    
    # Guardar resultados en un archivo
    output_file = f"{domain_or_ip.replace('http://', '').replace('https://', '').replace('.', '_')}.txt"
    with open(output_file, 'w') as file:
        if domains:
            print(f"\n{Fore.GREEN}Dominios encontrados en el mismo servidor que {domain_or_ip}:{Style.RESET_ALL}")
            for i, domain in enumerate(domains, start=1):
                # Obtener el estado HTTP y CMS
                status_code, cms = get_http_status_and_cms(domain)
                
                # Verificar si el estado es un número y aplicar colores apropiados
                if isinstance(status_code, int):
                    if status_code == 200:
                        status_display = f"{Fore.GREEN + Style.BRIGHT}{status_code}{Style.RESET_ALL}"
                    elif 300 <= status_code < 400:
                        status_display = f"{Fore.YELLOW + Style.BRIGHT}{status_code}{Style.RESET_ALL}"
                    elif 400 <= status_code < 500:
                        status_display = f"{Fore.RED + Style.BRIGHT}{status_code}{Style.RESET_ALL}"
                    else:
                        status_display = f"{Fore.RED + Style.BRIGHT}[ {status_code} ]{Style.RESET_ALL}"
                else:
                    status_display = f"{Fore.RED}[ No accesible ]{Style.RESET_ALL}"
                
                cms_display = cms if cms != "Desconocido" else "???"

                # Imprimir con formato alineado
                print(f"{Fore.CYAN}[ {i:03} ]{Style.RESET_ALL} -- {domain.ljust(30)} -- [ {status_display} ] -- [ {cms_display} ]")
                
                # Guardar en el archivo
                file.write(f"{domain} - Status: {status_code}, CMS: {cms_display}\n")
            print(f"\n{Fore.GREEN}Resultados guardados en el archivo: {output_file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No se encontraron dominios en el mismo servidor. Resultados guardados en el archivo: {output_file}{Style.RESET_ALL}")
            file.write(f"No se encontraron dominios en el mismo servidor que {domain_or_ip}.")
    
    return domains

# Ejecución principal
if __name__ == "__main__":
    print(BANNER)
    try:
        while True:
            domain_or_ip = input(f"{Fore.YELLOW}Ingrese el dominio o IP para el Reverse IP Domain Check: {Style.RESET_ALL}").strip()
            if domain_or_ip:
                reverse_ip_domain_check(domain_or_ip)
                break
            else:
                print(f"{Fore.RED}Entrada vacía, por favor ingrese un dominio o IP válido.{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Proceso cancelado por el usuario. Saliendo...{Style.RESET_ALL}")
