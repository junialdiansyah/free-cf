from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import sys
from contextlib import contextmanager

console = Console()

@contextmanager
def show_loading(message: str, spinner: str = "dots"):
    """
    Context manager to show a loading spinner.
    Usage:
        with ui.show_loading("Fetching data..."):
            api.do_something()
    """
    with console.status(f"[bold cyan]{message}[/bold cyan]", spinner=spinner):
        yield

def create_progress():
    """
    Returns a configured Progress object.
    Usage:
        with ui.create_progress() as progress:
            task = progress.add_task("Processing...", total=10)
            ...
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )

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

def print_handshake_result(idx: int, alias: str, success: bool, latency: float, message: str):
    if success:
        console.print(f"[bold green]#{idx} {alias}[/bold green]: [green]✓ {message}[/green] [dim]({latency:.1f}ms)[/dim]")
    else:
        console.print(f"[bold red]#{idx} {alias}[/bold red]: [red]✗ {message}[/red]")

def print_reliability_result(idx: int, alias: str, stats: dict):
    if stats['success']:
        # Color coding based on latency for the METRICS only
        avg = stats['avg_latency']
        lat_color = "green" if avg < 150 else "yellow" if avg < 300 else "red"
        
        # Success status is ALWAYS green
        console.print(
            f"[bold green]#{idx} {alias}[/bold green]: "
            f"[bold green]✓ {stats['msg']}[/bold green] "
            f"[dim]Avg:[/dim] [bold {lat_color}]{avg:.0f}ms[/bold {lat_color}] "
            f"[dim]Jitter:[/dim] {stats['jitter']:.0f}ms "
            f"[dim]Rate:[/dim] {stats['success_rate']}%"
        )
    else:
        console.print(f"[bold red]#{idx} {alias}[/bold red]: [red]✗ {stats['msg']}[/red] (0% Success)")

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
        title="[bold]v2.1[/bold]",
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
    menu_table.add_row("[cyan]6[/cyan]", "Manage Presets (Profiles)")
    menu_table.add_row("[dim]0[/dim]", "[dim]Exit[/dim]")
    
    console.print(Panel(menu_table, title="[bold white]Menu Options[/bold white]", border_style="blue", padding=(0, 1)))
    
    choice = Prompt.ask("\nSelect Option", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")
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
    
    p_table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    p_table.add_column("ID", justify="right", style="dim", width=4)
    p_table.add_column("Protocol", style="cyan")
    
    p_table.add_row("1", "Trojan")
    p_table.add_row("2", "VLESS")
    p_table.add_row("3", "Shadowsocks")
    
    console.print(Panel(p_table, title="[bold white]Select Protocols[/bold white]", border_style="blue", padding=(0, 1)))
    console.print("[dim]Enter choices (comma separated, e.g. 1,2)[/dim]")
    
    choices = Prompt.ask("Choice", default="1,2")
    mapping = {"1": "trojan", "2": "vless", "3": "ss"}
    for c in choices.split(","):
        if c.strip() in mapping:
            protocols.append(mapping[c.strip()])
    
    # Ports
    ports = []
    
    pt_table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    pt_table.add_column("ID", justify="right", style="dim", width=4)
    pt_table.add_column("Port", style="cyan")
    
    pt_table.add_row("1", "443 (TLS)")
    pt_table.add_row("2", "80  (Data)")
    
    console.print(Panel(pt_table, title="[bold white]Select Ports[/bold white]", border_style="blue", padding=(0, 1)))
    console.print("[dim]Enter choices (comma separated, e.g. 1)[/dim]")
    
    choices = Prompt.ask("Choice", default="1")
    mapping = {"1": "443", "2": "80"}
    for c in choices.split(","):
        if c.strip() in mapping:
            ports.append(mapping[c.strip()])
            
    limit = IntPrompt.ask("\nLimit Results", default=10)
    
    return protocols, ports, limit

def select_worker_domain(domains_with_status: list) -> str:
    """
    Select a worker domain from a list of (domain, status) tuples.
    """
    if not domains_with_status:
        return "" 
    
    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column("No.", justify="right", style="dim", width=4)
    table.add_column("Domain", style="cyan")
    table.add_column("Status", justify="left")
    
    for idx, (domain, status) in enumerate(domains_with_status, 1):
        status_style = "bold green" if status == "ACTIVE" else "bold red"
        icon = "✅" if status == "ACTIVE" else "❌"
        table.add_row(str(idx), domain, f"[{status_style}]{status}[/{status_style}] {icon}")
        
    console.print(Panel(table, title="[bold white]Select Worker Domain[/bold white]", border_style="blue", padding=(0, 1)))
    
    choice = IntPrompt.ask("Select Domain", default=1)
    if 1 <= choice <= len(domains_with_status):
        return domains_with_status[choice-1][0]
        
    print_error("Invalid selection, using first option.")
    return domains_with_status[0][0]

def select_bug_host(hosts: list) -> str:
    if not hosts:
        console.print("[yellow]Could not fetch bug hosts. Please enter manually.[/yellow]")
        return Prompt.ask("Bug Host / SNI", default="")

    table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Host", style="cyan")
    
    for idx, host in enumerate(hosts, 1):
        table.add_row(f"{idx}", host)
    
    table.add_row(f"{len(hosts) + 1}", "[yellow]Manual Input[/yellow]")

    console.print(Panel(table, title="[bold white]Select Bug Host[/bold white]", border_style="blue", padding=(0, 1)))

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

    table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Region", style="white")
    table.add_column("Count", justify="right", style="dim")
    
    table.add_row("0", "[bold white]ALL REGIONS[/bold white] (Any)", "")
    
    region_map = {}
    for idx, region in enumerate(regions, 1):
        code = region.get("code", "UNK")
        count = region.get("count", 0)
        flag = region.get("flag", " ")
        full_name = get_country_name(code)
        
        table.add_row(f"{idx}", f"{flag} {full_name}", f"({count})")
        region_map[str(idx)] = code

    console.print(Panel(table, title="[bold white]Select Region(s)[/bold white]", border_style="blue", padding=(0, 1)))

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

    table = Table(show_header=False, box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("ISP", style="magenta")
    table.add_column("Count", justify="right", style="dim")
    
    table.add_row("0", "[bold white]ALL ISPs[/bold white]", "")
    
    org_map = {}
    for idx, org in enumerate(available_orgs, 1):
        name = org.get("name", "Unknown")
        count = org.get("count", 0)
        name_trunc = (name[:40] + '..') if len(name) > 40 else name
        
        table.add_row(f"{idx}", name_trunc, f"({count})")
        org_map[str(idx)] = name

    console.print(Panel(table, title="[bold white]Select ISP(s)[/bold white]", border_style="blue", padding=(0, 1)))

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

def manage_workers_menu(workers: list, active_idx: int) -> tuple[str, str, str]:
    """
    Displays worker management menu.
    Returns (action, name, url) 
    actions: 'add', 'switch', 'delete', 'back'
    """
    console.print("\n[bold blue]Worker Management[/bold blue]\n")
    
    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Name", style="white")
    table.add_column("URL", style="cyan")
    table.add_column("Status", justify="center")
    
    for idx, w in enumerate(workers):
        status = "[bold green]ACTIVE[/bold green]" if idx == active_idx else ""
        table.add_row(str(idx + 1), w['name'], w['url'], status)
        
    console.print(table)
    console.print("\nOptions:")
    console.print("[cyan]1[/cyan]. Add New Worker")
    console.print("[cyan]2[/cyan]. Switch Active Worker")
    console.print("[cyan]3[/cyan]. Delete Worker")
    console.print("[dim]0[/dim]. Back")
    
    choice = Prompt.ask("\nSelect Option", choices=["0", "1", "2", "3"], default="0")
    
    if choice == "0":
        return "back", "", ""
        
    elif choice == "1":
        name = Prompt.ask("Worker Name")
        url = Prompt.ask("Worker URL")
        return "add", name, url
        
    elif choice == "2":
        idx = IntPrompt.ask("Enter ID to switch to")
        return "switch", str(idx - 1), ""
        
    elif choice == "3":
        idx = IntPrompt.ask("Enter ID to delete")
        return "delete", str(idx - 1), ""
    
    return "back", "", ""

def manage_profiles_menu(profiles: dict) -> tuple[str, str]:
    """
    Displays profile management menu.
    Returns (action, profile_name)
    actions: 'load', 'delete', 'back'
    """
    console.print("\n[bold blue]Saved Profiles (Presets)[/bold blue]\n")
    
    if not profiles:
        console.print("[dim italic]No profiles saved yet.[/dim italic]")
        console.print("\n[dim]To save a profile, generate a config first, then choose 'Save as Profile'[/dim]")
        Prompt.ask("\nPress Enter to go back...")
        return "back", ""
    
    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Profile Name", style="cyan")
    table.add_column("Details", style="white")
    
    profile_names = list(profiles.keys())
    
    for idx, name in enumerate(profile_names, 1):
        p = profiles[name]
        details = f"{p.get('bug_host','')} | {','.join(p.get('regions',[]))} | {len(p.get('protocols',[]))} Protos"
        table.add_row(str(idx), name, details)
        
    console.print(table)
    console.print("\nOptions:")
    console.print("[green]1[/green]. Load Profile")
    console.print("[red]2[/red]. Delete Profile")
    console.print("[dim]0[/dim]. Back")
    
    choice = Prompt.ask("\nSelect Option", choices=["0", "1", "2"], default="0")
    
    if choice == "0":
        return "back", ""
        
    elif choice == "1":
        idx = IntPrompt.ask("Enter Profile ID to Load", default=1)
        if 1 <= idx <= len(profile_names):
            return "load", profile_names[idx-1]
            
    elif choice == "2":
        idx = IntPrompt.ask("Enter Profile ID to Delete", default=1)
        if 1 <= idx <= len(profile_names):
            if Prompt.ask(f"Are you sure you want to delete '{profile_names[idx-1]}'?", choices=["y", "n"]) == "y":
                return "delete", profile_names[idx-1]
    
    return "back", ""
