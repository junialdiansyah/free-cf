import sys
import os

# Add the parent directory to sys.path to ensure module imports work correctly
# regardless of where the script is run from
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.config import ConfigManager
from app.api import WorkerAPI
import app.ui as ui
from rich.prompt import Prompt

def main():
    # Force UTF-8 for Windows consoles to support emojis
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    ui.clear_screen()
    ui.print_banner()
    
    config_mgr = ConfigManager()
    worker_url = config_mgr.get_worker_url()
    
    if not worker_url:
        ui.console.print("\n[bold yellow]No Worker URL configured![/bold yellow]")
        worker_url = Prompt.ask("Enter your Cloudflare Worker URL (e.g., https://my-worker.workers.dev)")
        config_mgr.save_worker_url(worker_url)
        ui.print_success("Configuration saved!")
    
    api = WorkerAPI(worker_url)
    
    while True:
        try:
            choice = ui.get_menu_choice()
            
            if choice == "0":
                ui.console.print("\n[bold]Goodbye![/bold]")
                break
                
            elif choice == "1": # Check Regions
                ui.console.print("\n[dim]Fetching regions...[/dim]")
                data = api.get_regions()
                ui.display_regions(data)
                
            elif choice == "2": # Generate Config
                # 1. Get Generation Params (Host, Protocol, Port, Limit)
                bug_host, protocols, ports, limit = ui.get_generation_params()
                
                # 2. Fetch Regions for Selection
                ui.console.print("\n[dim]Fetching active regions...[/dim]")
                region_data = api.get_regions()
                
                # 3. Select Region
                selected_regions = ui.select_region(region_data)
                
                # 4. Select ISP (If a specific region is selected)
                selected_orgs = ["ALL"]
                if selected_regions != ["ALL"] and len(selected_regions) == 1:
                    # If user selected exactly one specific region, allow ISP filtering
                    selected_orgs = ui.select_isp(selected_regions[0], region_data)
                
                ui.console.print(f"\n[dim]Generating configuration for {selected_regions[0]} / {selected_orgs[0]}...[/dim]")
                result = api.generate_config(
                    bug_host=bug_host,
                    protocols=protocols,
                    ports=ports,
                    regions=selected_regions,
                    orgs=selected_orgs,
                    limit=limit
                )
                
                if result.startswith("Error"):
                    ui.print_error(result)
                else:
                    ui.console.print(ui.Panel(result, title="Generated Configuration", border_style="green"))
                    ui.print_success("Configuration generated successfully!")
            
            elif choice == "3": # My IP
                ui.console.print("\n[dim]Fetching IP info...[/dim]")
                data = api.get_my_ip()
                ui.console.print_json(data=data)
                
            elif choice == "4": # Update URL
                new_url = Prompt.ask("Enter new Worker URL", default=worker_url)
                config_mgr.save_worker_url(new_url)
                worker_url = new_url
                api = WorkerAPI(worker_url)
                ui.print_success("Configuration updated!")
                
            Prompt.ask("\nPress Enter to continue...")
            ui.clear_screen()
            ui.print_banner()
            
        except KeyboardInterrupt:
            ui.console.print("\n[bold]Goodbye![/bold]")
            break
        except Exception as e:
            ui.print_error(str(e))
            Prompt.ask("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
