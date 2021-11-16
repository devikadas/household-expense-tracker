from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import datetime
import  mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
)

connector = mydb.cursor()
connector.execute("CREATE DATABASE IF NOT EXISTS ExpenseTrackerDatabase")
connector.execute("USE ExpenseTrackerDatabase")
connector.execute(
	'CREATE TABLE IF NOT EXISTS ExpenseTracker (ID INT NOT NULL AUTO_INCREMENT, Date DATE, Category TEXT, SubCategory TEXT, Amount FLOAT, ModeOfPayment TEXT, PRIMARY KEY (ID))'
)

# Functions
def view_expense_info():
	global table, date, category, subCategory, amnt, MoP
	selected_expense = table.item(table.focus())
	values = selected_expense['values']
	expense_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))
	date.set_date(expense_date) ; category.set(values[2]) ; subCategory.set(values[3]) ; amnt.set(values[4]) ; MoP.set(values[5])

def clear_fields():
	global table, date, category, subCategory, amnt, MoP
	today_date = datetime.date.today()
	subCategory.set('') ; category.set('') ; amnt.set('') ; MoP.set('Cash'), date.set_date(today_date)
	table.selection_remove(*table.selection())

def delete_expense():
	if not table.selection():
		mb.showerror('Error', 'Please select an expense to delete!')
		return
	selected_expense = table.item(table.focus())
	values_selected = selected_expense['values']
	surety = mb.askyesno('Confirmation', 'Are you sure you want to delete the record?')
	if surety:
		connector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % values_selected[0])
		mydb.commit()
		list_selected_expenses()
		mb.showinfo('Info', 'The expense has been deleted successfully')

def delete_all_expenses():
	surety = mb.askyesno('Confirmation', 'Are you sure you want to delete all the expenses from the database?')
	if surety:
		table.delete(*table.get_children())
		connector.execute('DELETE FROM ExpenseTracker')
		mydb.commit()
		clear_fields()
		list_selected_expenses()
		mb.showinfo('Info', 'All expenses were deleted successfully')

def add_expense():
	global date, category, subCategory, amnt, MoP, connector
	if not date.get() or not category.get() or not subCategory.get() or not amnt.get() or not MoP.get():
		mb.showerror('Error', "Please fill all the missing fields!")
	else:
		connector.execute(
		'INSERT INTO ExpenseTracker (Date, Category, SubCategory, Amount, ModeOfPayment) VALUES (%s, %s, %s, %s, %s)',
		(date.get_date(), category.get(), subCategory.get(), amnt.get(), MoP.get()))
		mydb.commit()
		clear_fields()
		list_selected_expenses()
		mb.showinfo('Info', 'The expense has been added to the database')

def edit_expense():
	global table

	def edit_existing_expense():
		global table, date, amnt, subCategory, category, MoP, connector
		selected_expense = table.item(table.focus())
		contents = selected_expense['values']
		connector.execute('UPDATE ExpenseTracker SET Date = %s, Category = %s, SubCategory = %s, Amount = %s, ModeOfPayment = %s WHERE ID = %s',
		                  (date.get_date(), category.get(), subCategory.get(), amnt.get(), MoP.get(), contents[0]))
		mydb.commit()
		clear_fields()
		list_selected_expenses()
		mb.showinfo('Info', 'Expense record has been updated')
		edit_btn.destroy()
		cancel_btn.destroy()
		return

	def cancel_edit():
		clear_fields()
		edit_btn.destroy()
		cancel_btn.destroy()

	if not table.selection():
		mb.showerror('Error', 'Please select an expense to edit!')
		return
	view_expense_info()
	edit_btn = Button(data_entry_frame, text='Edit Expense', font=button_font, width=30, bg=buttons_bg, command=edit_existing_expense)
	edit_btn.place(x=10, y=340)
	cancel_btn = Button(data_entry_frame, text='Cancel', font=button_font, width=30, bg=buttons_bg, command=cancel_edit)
	cancel_btn.place(x=10, y=400)

def list_selected_expenses():
	global table, fromDate, toDate, totalExpense, connector
	table.delete(*table.get_children())
	connector.execute('SELECT * FROM ExpenseTracker WHERE Date BETWEEN %s AND %s', (fromDate.get_date(), toDate.get_date()))
	data = connector.fetchall()
	totalExp = get_total_expense()
	totalExpense.set(totalExp)
	for values in data:
		table.insert('', END, values=values)

def get_total_expense():
	global fromDate, toDate, connector
	connector.execute('SELECT ROUND(SUM(Amount), 2) from ExpenseTracker WHERE Date BETWEEN %s AND %s', (fromDate.get_date(), toDate.get_date()))
	totalExpense = connector.fetchone()[0]
	return totalExpense

# Backgrounds and Fonts
data_entry_frame_bg = 'Lavender'
buttons_frame_bg = 'WhiteSmoke'
buttons_bg = 'LightSkyBlue'

label_font = ('Calibri', 12)
entry_font = ('Calibri', 12)
button_font = ('Calibri', 13)
total_font = ('Calibri', 14)

# Initializing the GUI window
root = Tk()
root.title('Household Expense Tracker')
root.geometry('1200x550')
root.resizable(0, 0)

Label(root, text='HOUSEHOLD EXPENSE TRACKER', font=('Calibri', 15, 'bold'), bg=buttons_bg).pack(side=TOP, fill=X)

# Variables
category = StringVar()
subCategory = StringVar()
amnt = DoubleVar()
MoP = StringVar(value='Cash')
fromDate = DateEntry()
toDate = DateEntry()
totalExpense = DoubleVar()

# Frames
data_entry_frame = Frame(root, bg=data_entry_frame_bg)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root, bg=buttons_frame_bg)
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

table_frame = Frame(root)
table_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

# Data Entry Frame
Label(data_entry_frame, text='Date (M/DD/YY):', font=label_font, bg=data_entry_frame_bg).place(x=10, y=50)
date = DateEntry(data_entry_frame, date=datetime.date.today(), font=entry_font)
date.place(x=160, y=50)

Label(data_entry_frame, text='Category:', font=label_font, bg=data_entry_frame_bg).place(x=10, y=100)
Entry(data_entry_frame, font=entry_font, width=15, text=category).place(x=160, y=100)

Label(data_entry_frame, text='Sub Category:', font=label_font, bg=data_entry_frame_bg).place(x=10, y=150)
Entry(data_entry_frame, font=entry_font, width=15, text=subCategory).place(x=160, y=150)

Label(data_entry_frame, text='Amount:', font=label_font, bg=data_entry_frame_bg).place(x=10, y=200)
Entry(data_entry_frame, font=entry_font, width=14, text=amnt).place(x=160, y=200)

Label(data_entry_frame, text='Mode of Payment:', font=label_font, bg=data_entry_frame_bg).place(x=10, y=250)
mopOptions = OptionMenu(data_entry_frame, MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay'])
mopOptions.place(x=160, y=250)
mopOptions.configure(width=10, font=entry_font)

Button(data_entry_frame, text='Add', command=add_expense, font=button_font, width=30, bg=buttons_bg).place(x=10, y=340)

Button(data_entry_frame, text='Clear', command=clear_fields, font=button_font, width=30, bg=buttons_bg).place(x=10, y=400)

# Buttons Frame
Button(buttons_frame, text='Edit', command=edit_expense, font=button_font, width=25, bg=buttons_bg).place(x=30,y=15)

Button(buttons_frame, text='Delete', command=delete_expense, font=button_font, width=25, bg=buttons_bg).place(x=335, y=15)

Button(buttons_frame, text='Delete All', command=delete_all_expenses, font=button_font, width=25, bg=buttons_bg).place(x=640, y=15)

Label(buttons_frame, text='From', font=label_font).place(x=30, y=70)
fromDate = DateEntry(buttons_frame, date=datetime.date.today(), day=1, font=entry_font)
fromDate.place(x=70, y=70)

Label(buttons_frame, text='To', font=label_font).place(x=200, y=70)
toDate = DateEntry(buttons_frame, date=datetime.date.today(), font=entry_font)
toDate.place(x=230, y=70)

Button(buttons_frame, text='View', command=list_selected_expenses, font=button_font, width=20, bg=buttons_bg).place(x=380, y=65)

Label(buttons_frame, text='Total: ', font=total_font).place(x=640, y=70)
Label(buttons_frame, textvariable=totalExpense, font=total_font).place(x=690, y=70)

# Treeview Frame
table = ttk.Treeview(table_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Category', 'Sub Category', 'Amount', 'Mode of Payment'))

X_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)

table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

table.heading('ID', text='S No.', anchor=CENTER)
table.heading('Date', text='Date', anchor=CENTER)
table.heading('Category', text='Category', anchor=CENTER)
table.heading('Sub Category', text='Sub Category', anchor=CENTER)
table.heading('Amount', text='Amount', anchor=CENTER)
table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1', width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)  # Date column
table.column('#3', width=150, stretch=NO)  # Category column
table.column('#4', width=325, stretch=NO)  # Sub Category column
table.column('#5', width=135, stretch=NO)  # Amount column
table.column('#6', width=125, stretch=NO)  # Mode of Payment column

table.place(relx=0, y=0, relheight=1, relwidth=1)

list_selected_expenses()

root.update()
root.mainloop()