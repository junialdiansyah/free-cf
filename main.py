import sys
import os
import urllib.parse

# Add the parent directory to sys.path to ensure module imports work correctly
# regardless of where the script is run from
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


import app.config as config
from app.api import WorkerAPI
import app.ui as ui
from rich.prompt import Prompt
from app.history import HistoryManager
from app.network import tcp_ping, check_domain_status
import pyperclip

def process_generated_result(result_tuple, bug_host=None):
    # Unpack tuple (result_content, subscription_url)
    if isinstance(result_tuple, tuple):
        result, sub_url = result_tuple
    else:
        # Fallback for error strings
        result = result_tuple
        sub_url = ""

    if result.startswith("Error"):
        ui.print_error(result)
    else:
        ui.console.print("\n[bold green]--- Generated Configuration ---[/bold green]\n")
        print(result)
        
        # Auto Copy to Clipboard
        try:
            pyperclip.copy(result)
            ui.console.print("\n[bold green]✓ Config copied to clipboard![/bold green]")
        except Exception as e:
            ui.console.print(f"\n[dim red]Failed to copy to clipboard: {e}[/dim red]")
            
        print()        
        if sub_url:
            ui.console.print(f"[bold yellow]Subscription Link:[/bold yellow] [underline]{sub_url}[/underline]")
            
            # Offer QR Code
            ui.console.print("\n[bold]Select QR Code to Display:[/bold]")
            ui.console.print("[cyan]1. Subscription Link[/cyan] (For importing via URL)")
            ui.console.print("[cyan]2. Raw Configuration[/cyan] (For direct scanning)")
            ui.console.print("[dim]0. Skip[/dim]")
            
            qr_choice = Prompt.ask("Choice", choices=["0", "1", "2"], default="0")
            
            if qr_choice == "1":
                ui.print_qrcode(sub_url)
            elif qr_choice == "2":
                # Split configs by newline to handle multiple links
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                
                if len(lines) > 1:
                    ui.console.print(f"\n[yellow]Multiple configs detected. Displaying QR codes separately to ensure scannability.[/yellow]")
                    
                    for i, line in enumerate(lines, 1):
                        ui.clear_screen()
                        ui.console.print(f"\n[bold green]Configuration {i}/{len(lines)}[/bold green]")
                        ui.console.print(f"[dim]{line[:60]}...[/dim]")
                        ui.print_qrcode(line)
                        if i < len(lines):
                            Prompt.ask("\nPress Enter for next QR...")
                else:
                    # Single config, safe to print
                    ui.print_qrcode(result)

        ui.console.print("\n[dim]Saving files...[/dim]")
        
        # Perform Real Proxy Handshake Test
        ui.console.print("\n[bold]Testing Proxy Handshake...[/bold]")
        
        # Split result into lines to test each config
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        
        from app.network import test_proxy_handshake
        
        for i, line in enumerate(lines, 1):
            if line.startswith("vless://") or line.startswith("trojan://"):
                # Extract a short alias from the hash/remark for display
                try:
                    alias = line.split('#')[-1]
                    alias = urllib.parse.unquote(alias)
                    if len(alias) > 20: alias = alias[:20] + ".."
                except:
                    alias = "Config"
                    
                success, latency, msg = test_proxy_handshake(line)
                ui.print_handshake_result(i, alias, success, latency, msg)
        
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

        # 3. Save sing-box.json (Converted)
        singbox_path = os.path.join(save_dir, "sing-box.json")
        try:
            from app.singbox import generate_singbox_config
            sb_json = generate_singbox_config(result)
            
            with open(singbox_path, "w", encoding="utf-8") as f:
                f.write(sb_json)
            ui.print_success(f"Sing-box config saved to {singbox_path}")
        except Exception as e:
            ui.print_error(f"Failed to save {singbox_path}: {e}")

def main():
    # Force UTF-8 for Windows consoles to support emojis
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    ui.clear_screen()
    ui.print_banner()
    
    # Static Configuration
    api = WorkerAPI(config.WORKER_URL)
    
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
                
            elif choice == "2": # Generate Configuration
                # 0. Fetch Worker Domains (App Domains)
                ui.console.print("\n[dim]Fetching worker domains...[/dim]")
                wd_data = api.get_worker_domains()
                w_domains = wd_data.get("domains", [])
                
                selected_app_domain = ""
                if len(w_domains) > 1:
                    ui.console.print("\n[dim]Checking domain health...[/dim]")
                    domain_status_list = []
                    for d in w_domains:
                        status = check_domain_status(d)
                        domain_status_list.append((d, status))
                    
                    selected_app_domain = ui.select_worker_domain(domain_status_list)
                    ui.console.print(f"[dim]Selected: {selected_app_domain}[/dim]")
                elif w_domains:
                    selected_app_domain = w_domains[0]

                # 0. Fetch Bug Hosts & Select (Standard)
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
                
                # Save to History
                history_data = {
                    "bug_host": selected_bug_host,
                    "protocols": protocols,
                    "ports": ports,
                    "regions": selected_regions,
                    "orgs": selected_orgs,
                    "limit": limit,
                    "app_domain": selected_app_domain
                }
                HistoryManager.save_last_config(history_data)

                result = api.generate_config(
                    bug_host=selected_bug_host,
                    protocols=protocols,
                    ports=ports,
                    regions=selected_regions,
                    orgs=selected_orgs,
                    limit=limit,
                    app_domain=selected_app_domain
                )
                
                process_generated_result(result, bug_host=selected_bug_host)

            elif choice == "3": # Generate from Last Used
                last_config = HistoryManager.load_last_config()
                if not last_config:
                    ui.print_error("No history found. Please generate a config first.")
                else:
                    ui.console.print("\n[bold cyan]Loading Last Used Configuration...[/bold cyan]")
                    ui.console.print_json(data=last_config)
                    
                    if Prompt.ask("\nProceed with these settings?", choices=["y", "n"], default="y") == "y":
                        result = api.generate_config(
                            bug_host=last_config.get("bug_host", ""),
                            protocols=last_config.get("protocols", ["vless"]),
                            ports=last_config.get("ports", ["443"]),
                            regions=last_config.get("regions", ["ALL"]),
                            orgs=last_config.get("orgs", ["ALL"]),
                            limit=last_config.get("limit", 1),
                            app_domain=last_config.get("app_domain", "")
                        )
                        process_generated_result(result, bug_host=last_config.get("bug_host", ""))
            
            elif choice == "4": # Instant Generate (Random 5)
                ui.console.print("\n[dim]Fetching bug hosts...[/dim]")
                domain_data = api.get_bug_hosts()
                bug_hosts = domain_data.get("domains", [])
                
                # Pick Random Bug Host if available
                import random
                selected_bug_host = ""
                if bug_hosts:
                    selected_bug_host = random.choice(bug_hosts)
                    ui.console.print(f"[dim]Randomly selected bug host: [cyan]{selected_bug_host}[/cyan][/dim]")
                
                ui.console.print("\n[dim]Generating 5 random configurations...[/dim]")
                
                result = api.generate_config(
                    bug_host=selected_bug_host,
                    protocols=["trojan", "vless"],
                    ports=["443", "80"],
                    regions=["ALL"],
                    orgs=["ALL"],
                    limit=5
                )
                
                process_generated_result(result, bug_host=selected_bug_host)

            elif choice == "5": # Check My IP
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
