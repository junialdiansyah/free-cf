from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, IntPrompt
import sys

console = Console()

def clear_screen():
    console.clear()

def print_banner():
    console.print(Panel.fit(
        "[bold cyan]INTERNET FREEDOM[/bold cyan]\n[white]Advanced VLESS & Trojan Generator CLI[/white]",
        border_style="blue",
        padding=(1, 4)
    ))

def print_error(msg):
    console.print(f"[bold red]Error:[/bold red] {msg}")

def print_success(msg):
    console.print(f"[bold green]Success:[/bold green] {msg}")

def get_menu_choice():
    console.print("\n[bold yellow]Menu Options:[/bold yellow]")
    console.print("1. [cyan]Check Available Regions[/cyan]")
    console.print("2. [cyan]Generate Configuration[/cyan]")
    console.print("3. [cyan]Check My IP[/cyan]")
    console.print("0. [red]Exit[/red]")
    return Prompt.ask("\n[bold]Select an option[/bold]", choices=["0", "1", "2", "3"], default="0")

def display_regions(data: dict):
    if "error" in data:
        print_error(data["error"])
        return

    total_proxies = data.get("total", 0)
    regions = data.get("regions", [])

    console.print(f"\n[bold]Total Active Proxies:[/bold] [green]{total_proxies}[/green]")

    table = Table(title="Available Regions", box=box.ROUNDED)
    table.add_column("Flag", justify="center")
    table.add_column("Country", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Top ISPs", style="magenta")

    for region in regions:
        orgs_str = ", ".join([f"{o['name']} ({o['count']})" for o in region.get('orgs', [])[:2]])
        table.add_row(
            region.get("flag", ""),
            region.get("code", "UNK"),
            str(region.get("count", 0)),
            orgs_str
        )
    
    console.print(table)

def get_generation_params():
    console.print("\n[bold]Configuration Generator[/bold]")
    
    bug_host = Prompt.ask("Bug Host / SNI (Leave empty to use Worker Domain)", default="")
    
    # Protocols
    protocols = []
    console.print("\nSelect Protocols (comma separated): [1] Trojan, [2] VLESS, [3] Shadowsocks")
    choices = Prompt.ask("Choice", default="1,2")
    mapping = {"1": "trojan", "2": "vless", "3": "ss"}
    for c in choices.split(","):
        if c.strip() in mapping:
            protocols.append(mapping[c.strip()])
    
    # Ports
    ports = []
    console.print("\nSelect Ports (comma separated): [1] 443 (TLS), [2] 80 (Data)")
    choices = Prompt.ask("Choice", default="1")
    mapping = {"1": "443", "2": "80"}
    for c in choices.split(","):
        if c.strip() in mapping:
            ports.append(mapping[c.strip()])
            
    limit = IntPrompt.ask("\nLimit Results", default=10)
    
    return bug_host, protocols, ports, limit

def select_region(data: dict) -> list[str]:
    """
    Interactive prompt to select regions.
    Returns a list of selected region codes (e.g. ['SG', 'ID']) or ['ALL'].
    """
    if "error" in data or "regions" not in data:
        return ["ALL"]

    regions = data.get("regions", [])
    if not regions:
        return ["ALL"]

    console.print("\n[bold]Select Region(s):[/bold]")
    console.print(f"0. [bold white]ALL REGIONS[/bold white] (Any available)")
    
    # Map index to region code
    region_map = {}
    for idx, region in enumerate(regions, 1):
        code = region.get("code", "UNK")
        count = region.get("count", 0)
        flag = region.get("flag", "")
        console.print(f"{idx}. {flag}  [cyan]{code}[/cyan] ({count} IPs)")
        region_map[str(idx)] = code

    input_str = Prompt.ask("\nEnter selection (comma separated numbers, e.g. 1,3)", default="0")
    
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
    """
    Interactive prompt to select ISPs from a provided list.
    Returns a list of selected ISPs or ['ALL'].
    """
    if not available_orgs:
        return ["ALL"]

    console.print(f"\n[bold]Select ISP(s):[/bold]")
    console.print(f"0. [bold white]ALL ISPs[/bold white]")
    
    org_map = {}
    for idx, org in enumerate(available_orgs, 1):
        name = org.get("name", "Unknown")
        count = org.get("count", 0)
        # Truncate long names
        display_name = (name[:30] + '..') if len(name) > 30 else name
        console.print(f"{idx}. [magenta]{display_name}[/magenta] ({count})")
        org_map[str(idx)] = name

    input_str = Prompt.ask("\nEnter selection (comma separated numbers, e.g. 1,2)", default="0")
    
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
