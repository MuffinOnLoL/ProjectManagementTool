import click
from rich.console import Console
from rich.table import Table
import json
from datetime import datetime


#This class handles the core functions such as adding, saving/loading tasks
# as well as maintaining the list in memory
class Task:
    #Initialize the task class and assign the file to the active json while loading the data
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.task_list = self.load_from_json()
        
    #Attempt to load data from json or create a new file if it doesnt exist
    def load_from_json(self):
        try:
            with open(self.json_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return [] #If file does not exist then create it
        
    #Save all existing entries to json file
    def save_to_json(self):
        with open(self.json_file, "w") as file:
            json.dump(self.task_list, file, indent = 4)
    
    #Add a new task to the list and generate a unique ID for each task
    def add_task(self, title: str, description: str, due_date: str, priority: str) -> None:
        #Validate the input to make sure they are correct
        
        #Make sure title isnt empty
        if not title:
            raise ValueError("Title can't be empty!")
        
        #Make sure priority is one of the valid choices
        if priority not in ["Low", "Medium", "High"]:
            raise ValueError("Priority must be 'Low', 'Medium', or 'High'")
    
        #Validate the date format (YYYY-MM-DD)
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Due date must be in the following format: YYYY-MM-DD")
    
        #Generate a unique ID for each new task
        next_id = max([task["id"] for task in self.task_list], default=0) + 1

        #Create a dictionary with all fields or add entries to fields
        task = {
            "id": next_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority
        }

        #Add task to memory list
        self.task_list.append(task)
        #save the updated list to the json
        self.save_to_json()

task_manager = Task("tasks.json")
console = Console()

#Define CLI group that is entry for all commands
#also groups nesting of subcommands (add, view, etc)
@click.group()
def cli():
    pass

@cli.command()
@click.option("--title",
                prompt = "Task Title", 
                help = "The title of the task"
                )
@click.option("--description",
              prompt = "Task Description",
              help = "A detailed description of the task"
              )
@click.option("--due-date", 
                prompt = "Due Date (YYY-MM-DD)", 
                help = "The due date for the task"
                )
@click.option("--priority", 
                type = click.Choice(["Low", "Medium", "High"], case_sensitive=False),
                prompt = "Task Priority",
                help = "The priority of the task"
                )
#Adds a new task and prompt for all details
#(Calls tasksManagers 'add_task' to actually add to list)
def add(title, description, due_date, priority):
    #Push the task creation to TaskManager and display success message
    #Error out and handle if an error occurs
    try:
        task_manager.add_task(title, description, due_date, priority)
        console.print(f"[green]Task successfully added![/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
#View all tasks currently inside list or a message if none exist
def view():
    if not task_manager.task_list:
        console.print("[yellow]No current tasks.[/yellow]")
        return
    
    #Create a Rich table to display/format list
    from rich.table import Table
    table = Table(title="Tasks")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Priority", style="green")
    table.add_column("Due Date", justify="right", style="yellow")

    #Actually add the data to the table
    for task in task_manager.task_list:
        table.add_row(str(task["id"]), task["title"], task["description"], task["priority"], task["due_date"])

    #Actually render to console
    console.print(table)

#CLI entry
if __name__ == "__main__":
    cli()