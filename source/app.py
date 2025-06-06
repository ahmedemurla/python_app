import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import os

products = []
inventory = []
users = []
order_details = []

def load_data():
    if len(products)>0:
        products.clear()
        inventory.clear()

    with open("products.txt", "r") as file:
        for line in file:
            cleaned_line = re.sub(r'\s*\|\s*', '|', line.strip())
            product = cleaned_line.split("|")

            products.append(product)

    with open("inventory.txt", "r") as file:
        for line in file:
            cleaned_line = re.sub(r'\s*\|\s*', '|', line.strip())
            quantity = cleaned_line.split("|")

            inventory.append(quantity)
    
    with open("users.txt", "r", encoding="UTF-8") as file:
        for line in file:
            cleaned_line = re.sub(r'\s*\|\s*', '|', line.strip())
            user = cleaned_line.split("|")

            users.append(user)

    with open("order_details.txt", "r") as file:
        for line in file:
            cleaned_line = re.sub(r'\s*\|\s*', '|', line.strip())
            details = cleaned_line.split("|")

            order_details.append(details)
    

def table_panel():
    root.withdraw()

    def onClose():
        root.deiconify()
        window.destroy()

    def search():
        to_search = searchbar.get()
        category = dropdown.get()

        for row in rows:
            for cell in row:
                cell.config(state="normal")
                cell.delete(0, tk.END)
                cell.config(state="readonly")

        match_index = 0
        for product in products:
            result = re.search(to_search, product[2], re.IGNORECASE)
            

            if result and category==product[1]:
                for i in range(4):
                    value = product[i] if i != 3 else product[i] + " лв."
                    entry = rows[match_index][i]
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(tk.END, value)
                    entry.config(state="readonly")
                match_index += 1
             

    window = tk.Toplevel()
    window.geometry(f"600x{len(products)*30}")
    window.title("Продукти")

    window.columnconfigure(0, weight=1)
    window.columnconfigure(5, weight=1)

    rows = []

    for i in range(len(products)):
        columns = []
        for j in range(4):

            width = 30 if j != 3 else 10
            value = products[i][j] if j != 3 else products[i][j] + " лв."

            e = tk.Entry(window, width=width, font=('Arial',10,'bold'))

            if j!=0:
                e.grid(row=i, column=j)
                
            e.insert(tk.END, value)
    
            e.config(state="readonly")

            columns.append(e)

        rows.append(columns)
    
    row_offset = len(products) + 1 

    tk.Label(window, text="Име на продукт:").grid(row=row_offset, column=1, columnspan=3, pady=10)

    searchbar = tk.Entry(window)
    searchbar.grid(row=row_offset+1, column=1, columnspan=3)

    tk.Button(window, text="Филтрирай", command=search).grid(row=row_offset + 4, column=1, columnspan=3, pady=10)

    tk.Label(window, text="Избери категория:").grid(row = row_offset + 2, column=1, columnspan=3)

    dropdown = ttk.Combobox(window, state="readonly")
    values = set()

    for product in products:
        values.add(product[1])
    
    dropdown["values"] = tuple(values)
    dropdown.current(0)
    dropdown.grid(row = row_offset + 3, column=1, columnspan=3, pady=(0, 20))

    window.protocol("WM_DELETE_WINDOW", onClose)

def order_panel():
    root.withdraw()

    basketList = []
    totalFloat = 0.0

    def onClose():
        root.deiconify()
        window.destroy()

    def showValue(e):
        a = shop.curselection()
        b = basket.curselection()

        if not a: 
            selection=b
            selected = basket.get(selection[0])
        if not b: 
            selection=a
            selected = shop.get(selection[0])
      
        for product in products:            
            if selected==product[2]:
                selected_value.config(text="")
                selected_value.config(text="Цена: " + str(float(product[3])) + " лв.")
                break
        
    
    def adjustTotal(item, direction:bool):
        nonlocal totalFloat

        if direction:
            totalFloat += float(item[3])
        else:
            totalFloat -= float(item[3])
        
        total_price.config(text="Обща цена: " + str(totalFloat) + " лв")

        

    def addToBasket():
        selection = shop.curselection()
        selected = shop.get(selection[0])
        
        for i in range(len(products)):

            if selected == products[i][2]:          
                if int(inventory[i][1]) < 1:
                    blocker = tk.Toplevel(window)
                    blocker.withdraw()
                    blocker.grab_set() 
                    messagebox.showerror(title="Грешка", message="За съжаление избраният продукт е изчерпан.")
                    blocker.grab_release()
                    blocker.destroy()
                    shop.delete(i)
                    break

                basketList.append(products[i])
                basket.insert(tk.END,selected)

                adjustTotal(products[i], True)
 
                inventory[i][1] = str(int(inventory[i][1]) - 1)
                               

    def removeFromBasket():
        selection = basket.curselection()

        basket.delete(selection)
        removed = basketList.pop(selection[0])

        adjustTotal(removed, False)

    def finalizeOrder():
        if all(len(v) != 0 for v in [name.get(), email.get(), tel.get(), city.get(), address.get()]):
            nonlocal totalFloat
            order_num = "[1]"
            user_num = len(users)+1
            matches = 0

            if os.path.exists('orders.txt'):
                with open("orders.txt", "r", encoding="UTF-8") as file:
                    for line in file:
                        match = re.search(r"\[+[0-9]+\]", line)
                        if match:
                            matches+=1
                    
                    order_num = f"[{matches+1}]"

            with open("orders.txt", "a", encoding="UTF-8") as file1, open("users.txt", "a", encoding="UTF-8") as file2, open("order_details.txt", "a") as file3:
                
                flag = False   

                file1.write("<===============КАСОВ БОН===============>\n")
                file1.write(f"Поръчка №: {order_num}\n")
                for item in basketList:
                    file1.write(f"Категория: {item[1]}\n")
                    file1.write(f"Наименование: {item[2]}\n")
                    file1.write(f"Ед. Цена: {item[3]} лв.\n")
                    file1.write("-----------------------------------------\n")
                file1.write(f"Обща цена: {totalFloat} лв.\n")
                file1.write(f"<================ПОЛУЧАТЕЛ==============>\n")
                file1.write(f"Име: {name.get()}\nИмейл: {email.get()}\nТелефонен номер: {tel.get()}\nГрад: {city.get()}\nАдрес: {address.get()}\n")
                file1.write("<=======================================>\n\n")
                
                for user in users:
                    if [name.get(), email.get(), tel.get(), city.get(), address.get()] == [user[1], user[2], user[3], user[4], user[5]]:
                        user_num = user[0]
                        flag=True

                if not flag:
                    file2.write(f"{str(len(users)+1)} | {name.get()} | {email.get()} | {tel.get()} | {city.get()} | {address.get()}\n")
                
                file3.write(f"{order_num[1:-1]} | {str(user_num)}\n")
                
            with open("inventory.txt", "w") as file:

                for row in inventory:

                    to_write = f"{row[0]} | {row[1]}"

                    file.write(to_write +"\n")


            messagebox.showinfo("Успешна поръчка.", "Поръчката ви беше приключена успешно!")
            basketList.clear()
            basket.delete(0,tk.END)
            totalFloat = 0
            total_price.config(text="")

            name.delete(0, tk.END)
            email.delete(0, tk.END)
            tel.delete(0, tk.END)
            city.delete(0, tk.END)
            address.delete(0, tk.END)

        else:
            messagebox.showerror("Грешка!", "Трябва да попълните всичките полета!")


    window = tk.Toplevel()
    window.geometry("1200x420")
    window.title("Поръчка")

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.columnconfigure(2, weight=1)
    window.columnconfigure(3, weight=1)
    window.columnconfigure(4, weight=1)
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)
    window.rowconfigure(2, weight=1)
    window.rowconfigure(3, weight=1)
    window.rowconfigure(4, weight=1)
    window.rowconfigure(5, weight=1)
    window.rowconfigure(6, weight=1)

    tk.Label(window, text="Име: ").grid(row=1, column=0, sticky="e")
    tk.Label(window, text="Email: ").grid(row=2, column=0, sticky="e")
    tk.Label(window, text="Телефон: ").grid(row=3, column=0, sticky="e")
    tk.Label(window, text="Град: ").grid(row=4, column=0, sticky="e")
    tk.Label(window, text="Адрес: ").grid(row=5, column=0, sticky="e")

    name = tk.Entry(window)
    name.grid(row=1, column=1, sticky="w")
    email = tk.Entry(window)
    email.grid(row=2, column=1, sticky="w")
    tel = tk.Entry(window)
    tel.grid(row=3, column=1, sticky="w")
    city = tk.Entry(window)
    city.grid(row=4, column=1, sticky="w")
    address = tk.Entry(window)
    address.grid(row=5, column=1, sticky="w")

    tk.Label(window, text="Магазин").grid(row=0, column=2)
    shop = tk.Listbox(window, width=50, height=20)
    shop_verscrlbar = ttk.Scrollbar(window, orient="vertical", command=shop.yview)
    shop.configure(yscrollcommand=shop_verscrlbar.set)
    shop.grid(row=1, column=2, rowspan=5, sticky="nsew")
    shop_verscrlbar.grid(row=1, column=2, rowspan=5, sticky="nse")
    shop.bind('<<ListboxSelect>>', showValue)

    tk.Label(window, text="Кошница").grid(row=0, column=4)
    basket = tk.Listbox(window, width=50, height=20)
    basket_verscrlbar = ttk.Scrollbar(window, orient="vertical", command=basket.yview)
    basket.configure(yscrollcommand=basket_verscrlbar.set)
    basket.grid(row=1, column=4, rowspan=5, sticky="nsew")
    basket_verscrlbar.grid(row=1, column=4, rowspan=5, sticky="nse")
    basket.bind('<<ListboxSelect>>', showValue)
    total_price = tk.Label(window, text="")
    total_price.grid(row=6, column=4)

    add_button = tk.Button(window, text="---> Добави в кошница --->", command=addToBasket)
    add_button.grid(row=2, column=3)

    remove_button = tk.Button(window, text="<--- Махни от кошница <---", command=removeFromBasket)
    remove_button.grid(row=4, column=3)

    order_button = tk.Button(window, text="Поръчвай", command=finalizeOrder)
    order_button.grid(row=5, column=3)

    selected_value = tk.Label(window, text="")
    selected_value.grid(row=1, column=3)


    for i in range(len(products)):
        if int(inventory[i][1]) > 0:
            shop.insert(tk.END, products[i][2])
        
    window.protocol("WM_DELETE_WINDOW", onClose)

def admin_panel():

    def decline():
        login.destroy()

    def confirm():
        try_user = usernameField.get()
        try_pass = passwordField.get()
        success = False

        with open("admin_credentials.txt", "r") as file:

            for line in file:
                user = re.search(r"^(.*?):", line)
                passw = re.search(r":(.*)$", line)
                
                if try_user == user.group(1) and try_pass == passw.group(1):
                    success = True
                    break
    
        if success:

            login.destroy()
            root.withdraw()

            nextId = len(products)+1
            sort_directions = {}

            def onClose():
                root.deiconify()
                window.destroy()

            def select(event):
                if len(table.selection()) <= 1:
                    warning.config(text="")

                    for k in table.selection():
                        items = table.item(k)["values"]

                        categoryField.delete(0, tk.END)
                        nameField.delete(0, tk.END)
                        priceField.delete(0, tk.END)
                        quantityField.delete(0, tk.END)

                        categoryField.insert(0, items[1])
                        nameField.insert(0, items[2])
                        priceField.insert(0, items[3])
                        quantityField.insert(0, items[4])
                else:
                    warning.config(text="Може да редактирате само един запис навъднъж!")
            
            def delete(event=""):
                response = messagebox.askokcancel(title="Потвърждение", message="Сигурни ли сте чи искаде да изтриете избраните записи?")
                
                if response:
                    for k in table.selection():
                        table.delete(k)

                        categoryField.delete(0, tk.END)
                        nameField.delete(0, tk.END)
                        priceField.delete(0, tk.END)
                        quantityField.delete(0, tk.END)

            def update():
                selected = (categoryField.get(), nameField.get(), priceField.get(), quantityField.get())
                passed = True
                
                if len(table.selection()) > 1:
                    passed = False
                    messagebox.showerror(title="Грешка", message="Повече от един елемент избран за редактиране!")

                if table.selection() and not all("" == s or s.isspace() for s in selected) and passed:

                    for k in table.selection():
                        
                        current_values = table.item(k, "values")

                        updated_values = (
                            current_values[0],
                            categoryField.get(),
                            nameField.get(),
                            priceField.get(),
                            quantityField.get()
                        )

                        table.item(k, text="", values=updated_values)
                    
                    categoryField.delete(0, tk.END)
                    nameField.delete(0, tk.END)
                    priceField.delete(0, tk.END)
                    quantityField.delete(0, tk.END)
                
                elif passed:
                    messagebox.showerror(title="Грешка", message="Не може да добавите празен запис!")

            def add():
                nonlocal nextId

                to_add = (str(nextId), categoryField.get(), nameField.get(), priceField.get(), quantityField.get())

                if not all("" == s or s.isspace() for s in (categoryField.get(), nameField.get(), priceField.get(), quantityField.get())):

                    table.insert(parent="", index=tk.END, values = to_add)

                    nextId+=1
                
                else:
                    messagebox.showerror(title="Грешка", message="Не може да добавите празен запис!")
            
            def save():
                response = messagebox.askyesno(title="Потвърждение", message="Сигурни ли сте чи искаде да запишете направените промени?")

                if response:
                    with open("products.txt", "w") as file:

                        for k in table.get_children():
                            row = table.item(k)["values"]

                            to_write = f"{row[0]} | {row[1]}\t| {row[2]}\t| {row[3]}"

                            file.write(to_write +"\n")

                    with open("inventory.txt", "w") as file:

                        for k in table.get_children():
                            row = table.item(k)["values"]

                            to_write = f"{row[0]} | {row[4]}"

                            file.write(to_write +"\n")
                    
                
                load_data()
            
            def clear():
                categoryField.delete(0, tk.END)
                nameField.delete(0, tk.END)
                priceField.delete(0, tk.END)
                quantityField.delete(0, tk.END)
        
                for k in table.selection():
                    table.selection_remove(k)

            def sort(col_index):
                reverse = sort_directions.get(col_index, False)
                temp = []

                for k in table.get_children():
                        row = table.item(k)["values"]
                        temp.append(row)

                try:
                    sorted_data = sorted(temp, key=lambda row: float(row[col_index]), reverse=reverse)
                except ValueError:
                    sorted_data = sorted(temp, key=lambda row: row[col_index].lower(), reverse=reverse)

                sort_directions[col_index] = not reverse

                for row in table.get_children():
                    table.delete(row)
                for row in sorted_data:
                    table.insert("", tk.END, values=row)

            window = tk.Toplevel(root)
            window.title("Админ панел")
            window.geometry("1200x600")

            window.columnconfigure(0, weight=1)
            window.columnconfigure(1, weight=1)
            window.columnconfigure(2, weight=1)
            window.columnconfigure(3, weight=1)
            window.rowconfigure(0, weight=1)
            window.rowconfigure(1, weight=1)
            window.rowconfigure(2, weight=1)
            window.rowconfigure(3, weight=1)
            window.rowconfigure(4, weight=1)
            window.rowconfigure(5, weight=1)
            window.rowconfigure(6, weight=1)
            window.rowconfigure(7, weight=1)
            window.rowconfigure(8, weight=1)
            window.rowconfigure(9, weight=1)
            
            columns = ("id", "category", "name", "price", "quantity")
            table = ttk.Treeview(window, columns=columns , show="headings")
            table.heading("id", text="ID", command=lambda: sort(0))
            table.column("id", minwidth=0, width=100, stretch=tk.NO)
            table.heading("category", text="Категория", command=lambda: sort(1))
            table.heading("name", text="Наименование", command=lambda: sort(2))
            table.heading("price", text="Цена", command=lambda: sort(3))
            table.heading("quantity", text="Наличност", command=lambda: sort(4))
            verscrlbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
            table.configure(yscrollcommand=verscrlbar.set)
            table.grid(row=0, column=0, rowspan=9, sticky="nsew")
            verscrlbar.grid(row=0, column=1, rowspan=9, sticky="nsw")

            for i in range(len(products)):
                table.insert(parent="", index=tk.END, values = (products[i][0], products[i][1], products[i][2], products[i][3], inventory[i][1]))
            
            table.bind("<Delete>", delete)
            table.bind("<<TreeviewSelect>>", select)

            tk.Label(window, text="Категория:").grid(row=0, column=2, sticky="e")
            tk.Label(window, text="Наименование:").grid(row=1, column=2, sticky="e")
            tk.Label(window, text="Цена:").grid(row=2, column=2, sticky="e")
            tk.Label(window, text="Наличност:").grid(row=3, column=2, sticky="e")

            categoryField = tk.Entry(window, width=30)
            categoryField.grid(row=0, column=3, sticky="w")
            nameField = tk.Entry(window, width=30)
            nameField.grid(row=1, column=3, sticky="w")
            priceField = tk.Entry(window, width=30)
            priceField.grid(row=2, column=3, sticky="w")
            quantityField = tk.Entry(window, width=30)
            quantityField.grid(row=3, column=3, sticky="w")


            updateButton = tk.Button(window, text="Обнови запис", width=20, command=update)
            updateButton.grid(row=4, column=2, columnspan=2)

            addButton = tk.Button(window, text="Добави запис", width=20, command=add)
            addButton.grid(row=5, column=2, columnspan=2)

            deleteButton = tk.Button(window, text="Изрий запис", width=20, command=delete)
            deleteButton.grid(row=6, column=2, columnspan=2)

            clearButton = tk.Button(window, text="Изчисти избора", width=20, command=clear)
            clearButton.grid(row=7, column=2, columnspan=2)

            saveButton = tk.Button(window, text="Запиши", width=20, command=save)
            saveButton.grid(row=8, column=2, columnspan=2)

            warning = tk.Label(window, text="", fg="red")
            warning.grid(row=9, column=0)

            window.protocol("WM_DELETE_WINDOW", onClose)
        
        else:
            messagebox.showerror("Грешка!", "Грешни входни данни!")


    login = tk.Toplevel(root)
    login.title("Вписване")
    login.geometry("300x200")

    login.columnconfigure(0, weight=1)
    login.columnconfigure(1, weight=1)
    login.rowconfigure(0, weight=1)
    login.rowconfigure(1, weight=1)
    login.rowconfigure(2, weight=1)

    tk.Label(login, text="Потреб. име:").grid(row= 0, column=0, sticky="e")
    tk.Label(login, text="Парола:").grid(row=1, column=0, sticky="e")

    usernameField = tk.Entry(login)
    usernameField.grid(row=0, column=1, sticky="w")

    passwordField = tk.Entry(login, show="*")
    passwordField.grid(row=1, column=1, sticky="w")

    login_button = tk.Button(login, text="Вписване", width=10, command=confirm)
    login_button.grid(row=2, column=0, sticky="e")

    back_button = tk.Button(login, text="Отказ", width=10, command=decline)
    back_button.grid(row=2, column=1)

load_data()

root = tk.Tk()
root.title("Начало")
root.geometry("1000x500")


button1 = tk.Button(root, text="Продукти", height=10, width=30, command=table_panel)
button2 = tk.Button(root, text="Поръчка", height=10, width=30, command=order_panel)
button3 = tk.Button(root, text="Админ Панел", height=10, width=30, command=admin_panel)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

button1.grid(row = 1, column = 0)
button2.grid(row = 1, column = 1)
button3.grid(row = 1, column = 2)

root.mainloop()