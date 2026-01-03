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
    
    # Static Configuration
    worker_url = ConfigManager.get_worker_url()
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
                # 0. Fetch Bug Hosts & Select
                ui.console.print("\n[dim]Fetching bug hosts...[/dim]")
                domain_data = api.get_bug_hosts()
                bug_hosts = domain_data.get("domains", [])
                
                selected_bug_host = ui.select_bug_host(bug_hosts)
                
                # 1. Get Generation Params (Protocol, Port, Limit)
                protocols, ports, limit = ui.get_generation_params()
                
                # 2. Fetch Regions for Selection
                ui.console.print("\n[dim]Fetching active regions...[/dim]")
                region_data = api.get_regions()
                
                # 3. Select Region(s)
                selected_regions = ui.select_region(region_data)
                
                # 4. Select ISP(s)
                selected_orgs = ["ALL"]
                
                # If "ALL" regions is NOT selected, we can filter ISPs available in the selected regions
                if "ALL" not in selected_regions:
                    # Aggregate potential ISPs from all selected regions
                    available_orgs = {}
                    
                    for r in region_data.get("regions", []):
                        if r.get("code") in selected_regions:
                            for o in r.get("orgs", []):
                                name = o.get("name")
                                count = o.get("count", 0)
                                if name in available_orgs:
                                    available_orgs[name] += count
                                else:
                                    available_orgs[name] = count
                    
                    # Convert back to list of dicts for UI
                    org_list = [{"name": k, "count": v} for k, v in available_orgs.items()]
                    # Sort by count desc
                    org_list.sort(key=lambda x: x['count'], reverse=True)
                    
                    if org_list:
                        selected_orgs = ui.select_isp(org_list)
                
                regions_display = ",".join(selected_regions)
                orgs_display = ",".join(selected_orgs)
                ui.console.print(f"\n[dim]Generating configuration for regions=[white]{regions_display}[/white], orgs=[white]{orgs_display}[/white]...[/dim]")
                
                result = api.generate_config(
                    bug_host=selected_bug_host,
                    protocols=protocols,
                    ports=ports,
                    regions=selected_regions,
                    orgs=selected_orgs,
                    limit=limit
                )
                
                if result.startswith("Error"):
                    ui.print_error(result)
                else:
                    ui.console.print("\n[bold green]--- Generated Configuration ---[/bold green]\n")
                    print(result)
                    print() # Empty line
                    
                    # Determine Save Paths
                    save_dir = "."
                    if os.path.exists("/sdcard"):
                        save_dir = "/sdcard"
                        
                    bug_path = os.path.join(save_dir, "bug.yaml")
                    clash_path = os.path.join(save_dir, "clash.yaml")
                    
                    # 1. Save bug.yaml (Raw Links)
                    try:
                        with open(bug_path, "w", encoding="utf-8") as f:
                            f.write(result)
                        ui.print_success(f"Raw config saved to {bug_path}")
                    except Exception as e:
                        ui.print_error(f"Failed to save {bug_path}: {e}")

                    # 2. Save clash.yaml (Converted)
                    try:
                        # Convert to Clash
                        from app.clash import generate_clash_config
                        clash_yaml = generate_clash_config(result)
                        
                        with open(clash_path, "w", encoding="utf-8") as f:
                            f.write(clash_yaml)
                        ui.print_success(f"Clash config saved to {clash_path}")
                    except Exception as e:
                        ui.print_error(f"Failed to save {clash_path}: {e}")
            
            elif choice == "3": # My IP
                ui.console.print("\n[dim]Fetching IP info...[/dim]")
                data = api.get_my_ip()
                ui.console.print_json(data=data)
                
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
