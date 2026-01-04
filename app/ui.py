from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, IntPrompt
import sys

console = Console()

COUNTRY_NAMES = {
    "SG": "Singapore", "ID": "Indonesia", "US": "United States", "JP": "Japan",
    "DE": "Germany", "NL": "Netherlands", "FR": "France", "GB": "United Kingdom",
    "CN": "China", "HK": "Hong Kong", "TW": "Taiwan", "KR": "South Korea",
    "IN": "India", "AU": "Australia", "CA": "Canada", "BR": "Brazil",
    "RU": "Russia", "UA": "Ukraine", "VN": "Vietnam", "TH": "Thailand",
    "MY": "Malaysia", "PH": "Philippines", "TR": "Turkey", "IT": "Italy",
    "ES": "Spain", "PT": "Portugal", "PL": "Poland", "FI": "Finland",
    "SE": "Sweden", "NO": "Norway", "DK": "Denmark", "CH": "Switzerland",
    "AE": "United Arab Emirates", "SA": "Saudi Arabia", "ZA": "South Africa",
    "IL": "Israel", "IR": "Iran", "EG": "Egypt", "BD": "Bangladesh",
    "PK": "Pakistan", "NP": "Nepal", "LK": "Sri Lanka", "MM": "Myanmar",
    "KH": "Cambodia", "LA": "Laos", "KZ": "Kazakhstan", "UZ": "Uzbekistan",
    "KG": "Kyrgyzstan", "TJ": "Tajikistan", "TM": "Turkmenistan", "MN": "Mongolia",
    "NZ": "New Zealand", "IE": "Ireland", "BE": "Belgium", "AT": "Austria",
    "CZ": "Czech Republic", "SK": "Slovakia", "HU": "Hungary", "RO": "Romania",
    "BG": "Bulgaria", "GR": "Greece", "HR": "Croatia", "SI": "Slovenia",
    "RS": "Serbia", "BA": "Bosnia and Herzegovina", "MK": "North Macedonia",
    "ME": "Montenegro", "AL": "Albania", "MD": "Moldova", "BY": "Belarus",
    "LV": "Latvia", "LT": "Lithuania", "EE": "Estonia", "IS": "Iceland",
    "MX": "Mexico", "AR": "Argentina", "CL": "Chile", "CO": "Colombia",
    "PE": "Peru", "VE": "Venezuela", "EC": "Ecuador", "BO": "Bolivia",
    "PY": "Paraguay", "UY": "Uruguay", "NG": "Nigeria", "KE": "Kenya",
    "GH": "Ghana", "TZ": "Tanzania", "UG": "Uganda", "MZ": "Mozambique",
    "ZW": "Zimbabwe", "MA": "Morocco", "DZ": "Algeria", "TN": "Tunisia",
    "LY": "Libya", "SD": "Sudan", "ET": "Ethiopia", "SO": "Somalia"
}

def get_country_name(code):
    return COUNTRY_NAMES.get(code.upper(), code)

from rich import box
from rich.align import Align
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.layout import Layout
import sys

console = Console()

# ... (COUNTRY_NAMES remains same)

def clear_screen():
    console.clear()

def print_error(msg):
    console.print(f"[bold red]Error:[/bold red] {msg}")

def print_success(msg):
    console.print(f"[bold green]Success:[/bold green] {msg}")

def print_qrcode(data: str):
    import qrcode
    
    console.print("\n[bold white]Scanning QR Code for Mobile:[/bold white]")
    console.print("[dim](Use 'Scan QR' in your V2Ray/Clash App)[/dim]")

    # Create QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2, # Smaller border for terminal
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    width = len(matrix)
    
    # Compact rendering using block characters
    # ▀ (Upper half) \u2580
    # ▄ (Lower half) \u2584
    # █ (Full block) \u2588
    
    # We invert colors for dark terminal: 
    # True (Data) -> White (█, ▀, ▄)
    # False (Empty/Quiet) -> Black (Space)
    
    lines = []
    for y in range(0, width, 2):
        line = ""
        for x in range(width):
            top = matrix[y][x]
            # Check bottom row existence
            bottom = matrix[y+1][x] if y + 1 < width else False
            
            if top and bottom:
                line += "█"
            elif top and not bottom:
                line += "▀"
            elif not top and bottom:
                line += "▄"
            else:
                line += " "
        lines.append(line)
        
    # Print logic
    # We explicitly style it white-on-black (or default terminal bg)
    for line in lines:
        console.print(line, style="white on black")

def print_ping_result(host: str, success: bool, latency: float):
    if success:
        console.print(f"[bold green]✓ Connected to {host}[/bold green] [dim]({latency:.1f}ms)[/dim]")
    else:
        console.print(f"[bold red]✗ Failed to connect to {host}[/bold red]")

def print_banner():
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_row("[bold blue]INTERNET FREEDOM[/bold blue]")
    grid.add_row("[dim]Advanced VLESS & Trojan Generator[/dim]")
    
    panel = Panel(
        grid,
        style="blue",
        border_style="blue",
        padding=(0, 2),
        title="[bold]v2.0[/bold]",
        title_align="right"
    )
    console.print(panel)

def get_menu_choice():
    menu_table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    menu_table.add_column("Option", style="cyan", justify="right", width=4)
    menu_table.add_column("Description", style="white")
    
    menu_table.add_row("[cyan]1[/cyan]", "Check Available Regions")
    menu_table.add_row("[cyan]2[/cyan]", "Generate Configuration")
    menu_table.add_row("[cyan]3[/cyan]", "Generate from Last Used")
    menu_table.add_row("[cyan]4[/cyan]", "Instant Generate (Random 5)")
    menu_table.add_row("[cyan]5[/cyan]", "Check Client IP")
    menu_table.add_row("[dim]0[/dim]", "[dim]Exit[/dim]")
    
    console.print(Panel(menu_table, title="[bold white]Menu Options[/bold white]", border_style="blue", padding=(0, 1)))
    
    choice = Prompt.ask("\nSelect Option", choices=["0", "1", "2", "3", "4", "5"], default="0")
    return choice

def display_regions(data: dict):
    if "error" in data:
        print_error(data["error"])
        return

    total_proxies = data.get("total", 0)
    regions = data.get("regions", [])

    console.print(f"\n[dim]Total Active Proxies:[/dim] [bold green]{total_proxies}[/bold green]")

    table = Table(box=box.SIMPLE, show_lines=False, expand=True)
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Region", style="white")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Top ISPs", style="dim")

    for idx, region in enumerate(regions, 1):
        code = region.get("code", "UNK")
        full_name = get_country_name(code)
        
        # Format: Flag Country (Code)
        flag = region.get("flag", "")
        display_country = f"{flag} {full_name} ({code})"
        
        orgs = region.get('orgs', [])[:2]
        orgs_str = ", ".join([o['name'] for o in orgs])
        
        table.add_row(
            str(idx),
            display_country,
            str(region.get("count", 0)),
            orgs_str
        )
    
    console.print(table)

def get_generation_params():
    console.print("\n[bold blue]Configuration Generator[/bold blue]")
    
    # Protocols
    protocols = []
    
    p_table = Table(show_header=False, box=None, padding=(0, 1))
    p_table.add_row("1.", "[cyan]Trojan[/cyan]")
    p_table.add_row("2.", "[cyan]VLESS[/cyan]")
    p_table.add_row("3.", "[cyan]Shadowsocks[/cyan]")
    
    console.print(Panel(p_table, title="Select Protocols", border_style="dim", width=40))
    console.print("[dim]Enter choices (comma separated, e.g. 1,2)[/dim]")
    
    choices = Prompt.ask("Choice", default="1,2")
    mapping = {"1": "trojan", "2": "vless", "3": "ss"}
    for c in choices.split(","):
        if c.strip() in mapping:
            protocols.append(mapping[c.strip()])
    
    # Ports
    ports = []
    
    pt_table = Table(show_header=False, box=None, padding=(0, 1))
    pt_table.add_row("1.", "[cyan]443[/cyan] (TLS)")
    pt_table.add_row("2.", "[cyan]80[/cyan]  (Data)")
    
    console.print(Panel(pt_table, title="Select Ports", border_style="dim", width=40))
    console.print("[dim]Enter choices (comma separated, e.g. 1)[/dim]")
    
    choices = Prompt.ask("Choice", default="1")
    mapping = {"1": "443", "2": "80"}
    for c in choices.split(","):
        if c.strip() in mapping:
            ports.append(mapping[c.strip()])
            
    limit = IntPrompt.ask("\nLimit Results", default=10)
    
    return protocols, ports, limit

def select_bug_host(hosts: list) -> str:
    if not hosts:
        console.print("[yellow]Could not fetch bug hosts. Please enter manually.[/yellow]")
        return Prompt.ask("Bug Host / SNI", default="")

    table = Table(show_header=False, box=None, padding=(0, 1))
    for idx, host in enumerate(hosts, 1):
        table.add_row(f"{idx}.", f"[cyan]{host}[/cyan]")
    
    table.add_row(f"{len(hosts) + 1}.", "[yellow]Manual Input[/yellow]")

    console.print(Panel(table, title="Select Bug Host", border_style="blue", expand=False))

    choice = IntPrompt.ask("Enter selection", default=1)
    
    if 1 <= choice <= len(hosts):
        return hosts[choice - 1]
    
    if choice == len(hosts) + 1:
        return Prompt.ask("Bug Host / SNI")
        
    print_error("Invalid selection, using first option.")
    return hosts[0]

def select_region(data: dict) -> list[str]:
    if "error" in data or "regions" not in data:
        return ["ALL"]

    regions = data.get("regions", [])
    if not regions:
        return ["ALL"]

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("0.", "[bold white]ALL REGIONS[/bold white] (Any)")
    
    region_map = {}
    for idx, region in enumerate(regions, 1):
        code = region.get("code", "UNK")
        count = region.get("count", 0)
        flag = region.get("flag", " ")
        full_name = get_country_name(code)
        
        table.add_row(f"{idx}.", f"{flag} {full_name}", f"[dim]({count})[/dim]")
        region_map[str(idx)] = code

    console.print(Panel(table, title="Select Region(s)", border_style="blue", expand=False))

    input_str = Prompt.ask("Enter selection (comma separated)", default="0")
    
    selected_codes = set()
    for choice in input_str.split(","):
        choice = choice.strip()
        if choice == "0":
            return ["ALL"]
        if choice in region_map:
            selected_codes.add(region_map[choice])
            
    if not selected_codes:
        print_error("Invalid selection, defaulting to ALL")
        return ["ALL"]
        
    return list(selected_codes)

def select_isp(available_orgs: list[dict]) -> list[str]:
    if not available_orgs:
        return ["ALL"]

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("0.", "[bold white]ALL ISPs[/bold white]")
    
    org_map = {}
    for idx, org in enumerate(available_orgs, 1):
        name = org.get("name", "Unknown")
        count = org.get("count", 0)
        name_trunc = (name[:28] + '..') if len(name) > 28 else name
        
        table.add_row(f"{idx}.", f"[magenta]{name_trunc}[/magenta]", f"({count})")
        org_map[str(idx)] = name

    console.print(Panel(table, title="Select ISP(s)", border_style="blue", expand=False))

    input_str = Prompt.ask("Enter selection (comma separated)", default="0")
    
    selected_names = set()
    for choice in input_str.split(","):
        choice = choice.strip()
        if choice == "0":
            return ["ALL"]
        if choice in org_map:
            selected_names.add(org_map[choice])
    
    if not selected_names:
        print_error("Invalid selection, defaulting to ALL")
        return ["ALL"]
        
    return list(selected_names)
