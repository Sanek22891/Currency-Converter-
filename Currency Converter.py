import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

# --- Настройки ---
API_KEY = 'YOUR_API_KEY'  # ЗАМЕНИТЕ НА СВОЙ КЛЮЧ
HISTORY_FILE = 'history.json'
# -------------------

def load_history():
    """Загружает историю из файла JSON."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    """Сохраняет историю в файл JSON."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def convert_currency():
    """Основная функция конвертации."""
    amount_str = entry_amount.get()
    from_currency = combo_from.get()
    to_currency = combo_to.get()

    # Валидация ввода
    if not amount_str or not from_currency or not to_currency:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной.")
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
        return

    # Запрос к API
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Проверка на ошибки HTTP
        data = response.json()
        
        if data.get('result') != 'success':
            raise Exception(data.get('error-type', 'Неизвестная ошибка API'))

        rate = data['conversion_rate']
        result = round(amount * rate, 2)
        
        # Обновление интерфейса
        label_result.config(text=f"Результат: {result} {to_currency}")

        # Сохранение в историю
        history = load_history()
        history.insert(0, {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "rate": rate,
            "result": result
        })
        save_history(history)
        update_history_table()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка сети", f"Не удалось подключиться к серверу: {e}")
    except Exception as e:
        messagebox.showerror("Ошибка API", str(e))

def update_history_table():
    """Обновляет таблицу истории."""
    for i in tree.get_children():
        tree.delete(i)
        
    history = load_history()
    for item in history:
        tree.insert("", tk.END, values=(
            item['date'],
            item['amount'],
            item['from'],
            item['to'],
            item['result']
        ))

# --- Создание окна ---
root = tk.Tk()
root.title("Currency Converter")
root.geometry("700x500")
root.resizable(False, False)

# --- Ввод данных ---
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Сумма:", font=('Arial', 12)).grid(row=0, column=0, padx=5)
entry_amount = tk.Entry(frame_input, font=('Arial', 12), width=15)
entry_amount.grid(row=0, column=1, padx=5)

tk.Label(frame_input, text="Из:", font=('Arial', 12)).grid(row=0, column=2, padx=5)
combo_from = ttk.Combobox(frame_input, values=['USD', 'EUR', 'GBP', 'RUB'], font=('Arial', 12), state='readonly')
combo_from.current(0)
combo_from.grid(row=0, column=3, padx=5)

tk.Label(frame_input, text="В:", font=('Arial', 12)).grid(row=0, column=4, padx=5)
combo_to = ttk.Combobox(frame_input, values=['USD', 'EUR', 'GBP', 'RUB'], font=('Arial', 12), state='readonly')
combo_to.current(1)
combo_to.grid(row=0, column=5, padx=5)

btn_convert = tk.Button(root, text="Конвертировать", command=convert_currency, font=('Arial', 12), bg="#4CAF50", fg="white")
btn_convert.pack(pady=10)

# --- Результат ---
label_result = tk.Label(root, text="Результат появится здесь", font=('Arial', 14))
label_result.pack(pady=10)

# --- История ---
frame_history = tk.Frame(root)
frame_history.pack(pady=20, fill='both', expand=True)

tree = ttk.Treeview(frame_history, columns=('Дата', 'Сумма', 'Из', 'В', 'Результат'), show='headings')
tree.heading('Дата', text='Дата')
tree.heading('Сумма', text='Сумма')
tree.heading('Из', text='Из')
tree.heading('В', text='В')
tree.heading('Результат', text='Результат')
tree.column('Дата', width=150)
tree.column('Сумма', width=80, anchor='center')
tree.column('Из', width=80, anchor='center')
tree.column('В', width=80, anchor='center')
tree.column('Результат', width=100, anchor='center')
tree.pack(fill='both', expand=True)

# Загрузка истории при старте
update_history_table()

root.mainloop()
