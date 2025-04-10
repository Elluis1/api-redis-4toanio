import tkinter as tk
from tkinter import messagebox
import redis;

r = redis.Redis(host='localhost',
                port=6379, decode_responses=True)

# Ahora que ya maneja los conocimientos básicos genere una lista con los
# capítulos de todas las temporadas de The Mandalorian, los cuales podrán ser
# alquilados para ver por una persona al mismo tiempo.

balance = 15000

episodes = {
    "S01": [
        "Chapter 1: The Mandalorian",
        "Chapter 2: The Child",
        "Chapter 3: The Sin",
        "Chapter 4: Sanctuary",
        "Chapter 5: The Gunslinger",
        "Chapter 6: The Prisoner",
        "Chapter 7: The Reckoning",
        "Chapter 8: Redemption"
    ],
    "S02": [
        "Chapter 9: The Marshal",
        "Chapter 10: The Passenger",
        "Chapter 11: The Heiress",
        "Chapter 12: The Siege",
        "Chapter 13: The Jedi",
        "Chapter 14: The Tragedy",
        "Chapter 15: The Believer",
        "Chapter 16: The Rescue"
    ],
    "S03": [
        "Chapter 17: The Apostate",
        "Chapter 18: The Mines of Mandalore",
        "Chapter 19: The Convert",
        "Chapter 20: The Foundling",
        "Chapter 21: The Pirate",
        "Chapter 22: Guns for Hire",
        "Chapter 23: The Spies",
        "Chapter 24: The Return"
    ]
}

def view_episodes():
    season = input("Enter the season (S01, S02, S03): ")
    if season in episodes:
        for key in r.keys(f"mandalorian:{season}:*"):
            print(key, "->", r.get(key))
    else:
        print("Invalid season. Please enter S01, S02, or S03.")

def rent_episode():
    season = input("Enter the season (S01, S02, S03): ")
    chapter = input("Enter the chapter: ")
    key = f"mandalorian:{season}:{chapter}"
    if r.exists(key):
        if r.get(key) == "available":
            r.setex(key, 240, "rented")
            print(f"You have rented {key}.")
        else:
            print(f"{key} is already rented.")
    else:
        print(f"{key} does not exist.")

sueldo = 15000

def payment_check():
    alquilers01 = 1000
    alquilers02 = 1500
    alquilers03 = 2000
    season = input("Enter the season (S01, S02, S03): ")
    chapter = input("Enter the chapter: ")
    key = f"mandalorian:{season}:{chapter}"
    if r.exists(key):
        if r.get(key) == "available":
            if season == "S01":
                total = alquilers01
            elif season == "S02":
                total = alquilers02
            elif season == "S03":
                total = alquilers03
            print(f"Your account have: {sueldo} pesos")
            print(f"Total payment for {key} is: {total}")
            input("Press Enter to continue...")
            r.setex(key, 86400, "rented")
            print(f"Your account now has: {sueldo - total} pesos")
        else:
            print(f"{key} is already rented.")

# Función para obtener los episodios desde Redis
def get_episodes():
    episodes = {}
    keys = r.keys("mandalorian:S*:*")
    
    for key in keys:
        parts = key.split(":")
        season, chapter = parts[1], parts[2]
        
        if season not in episodes:
            episodes[season] = []
        
        # Obtener el estado del capítulo desde Redis
        status = r.get(key) or "unknown"

        # Asegurar que no se repita "Chapter"
        if not chapter.startswith("Chapter"):
            chapter = f"Chapter {chapter}"

        episodes[season].append(f"{chapter} {status}")
    
    return episodes


# Función para mostrar los episodios disponibles
def show_episodes():
    season = season_var.get()
    listbox.delete(0, tk.END)
    
    keys = r.keys(f"mandalorian:{season}:*")
    for key in keys:
        chapter_number = key.split(":")[-1]
        status = r.get(key)
        status = status if status else "available"  # Si no existe, es disponible
        listbox.insert(tk.END, f"Chapter {chapter_number} - {status}")

        
# Función para alquilar un episodio
def rent_episode():
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        messagebox.showwarning("Warning", "Select an episode to rent")
        return
    
    season = season_var.get()
    chapter_number = selected.split(" - ")[0].split(" ")[1]
    key = f"mandalorian:{season}:{chapter_number}"
    
    status = r.get(key)
    if status and status == "available":
        r.setex(key, 240, "reserved")
        messagebox.showinfo("Success", f"Chapter {chapter_number} is now reserved for 4 minutes")
        show_episodes()
    else:
        messagebox.showerror("Error", "Episode is already rented or reserved")


# Función para confirmar el pago
def confirm_payment():
    global balance
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        messagebox.showwarning("Warning", "Select an episode to confirm payment")
        return
    
    season = season_var.get()
    chapter_number = selected.split(" - ")[0].split(" ")[1]
    key = f"mandalorian:{season}:{chapter_number}"
    
    if r.get(key) == "reserved":
        price = {"S01": 1000, "S02": 1500, "S03": 2000}.get(season, 0)
        if balance >= price:
            balance -= price
            r.set(key, "rented")
            messagebox.showinfo("Payment Success", f"{chapter_number} rented successfully! New balance: {balance} pesos")
            show_episodes()
        else:
            messagebox.showerror("Error", "Insufficient balance")
    else:
        messagebox.showerror("Error", "Episode is not reserved")

# Configuración de la UI
root = tk.Tk()
root.title("The Mandalorian - Episode Rental")
root.geometry("500x400")

season_var = tk.StringVar(value="S01")
season_menu = tk.OptionMenu(root, season_var, "S01", "S02", "S03")
season_menu.pack()

tk.Button(root, text="Show Episodes", command=show_episodes).pack()

listbox = tk.Listbox(root, width=50, height=10)
listbox.pack()

tk.Button(root, text="Rent Episode", command=rent_episode).pack()
tk.Button(root, text="Confirm Payment", command=confirm_payment).pack()

tk.Label(root, text=f"Balance: {balance} pesos").pack()

show_episodes()

root.mainloop()

# keys = r.keys("mandalorian:S*")  
# if keys:
#     r.delete(*keys)  # Borra todas las claves encontradas
#     print(f"Deleted {len(keys)} keys from Redis.")
    
# Subir capítulos a Redis con claves consistentes
# for season, chapters in episodes.items():
#     for chapter in chapters:
#         chapter_number = chapter.split(":")[0].replace("Chapter ", "")  
#         key = f"mandalorian:{season}:{chapter_number}"
#         r.set(key, "available")
#         print(f"Added {key} to Redis with value 'available'.")


# Punto 1
# view_episodes()

# Punto 2
# rent_episode()

# Punto 3
# payment_check()