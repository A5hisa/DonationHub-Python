import sqlite3
import os 
import datetime
import logging
import smtplib
from tkinter import *
from tkinter import messagebox, ttk
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Font
FONT_TITLE = ("Arial", 18, "bold")
FONT_THAI = ("Aria", 16, "normal")
FONT_THAI_DATA = ("Aria", 14, "normal")
FONT_THAI_10 = ("Aria", 10, "normal")
FONT_THAI_10_BOLD = ("Aria", 10, "bold")


# Log file Set Up
# log file & log config
log = "system.log"
logging.basicConfig(filename=log,
                    encoding="UTF-8",
                    format='%(asctime)s %(message)s',
                    datefmt="%d-%m-%Y %H:%M:%S",
                    level=logging.INFO)

# Database SetUp
database_name = "DonationHub.db"
Have_DB = False

# check files
files = os.listdir()
if database_name in files:
    Have_DB = True

# Create Database OR Connect Database
con = sqlite3.connect(database_name)
cur = con.cursor()

# Provinces list & ItemType list
PROVINCES = ["-",
    "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร",
    "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท",
    "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง",
    "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม",
    "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส",
    "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์",
    "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พะเยา", "พังงา",
    "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์",
    "แพร่", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน",
    "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง", "ระยอง",
    "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย",
    "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ",
    "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี",
    "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย",
    "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์",
    "อุทัยธานี", "อุบลราชธานี"
]

ITEM_TYPE = ["-", "เสื้อผ้า", "ของเล่นเด็ก", "หนังสือ", "ยารักษาโรค", "อาหารแห้ง", "อุปกรณ์การเรียน", "อุปกรณ์กีฬา", "เครื่องใช้ไฟฟ้า"]


# Function
# Create Table 
def create_table():
    if not Have_DB:
        try:
            # Create table Donation
            cur.execute('''CREATE TABLE "Donation" (
                "ID" INTEGER NOT NULL UNIQUE, 
                "TypeItem" TEXT NOT NULL, 
                "Item" TEXT NOT NULL,
                "Detail" TEXT NOT NULL,
                "Amount" INT NOT NULL,
                "DonatorName" TEXT NOT NULL, 
                "DateDonation"	TEXT NOT NULL,
                "Location" TEXT NOT NULL,
                "Contact" TEXT NOT NULL,
                "Status" TEXT NOT NULL,
                PRIMARY KEY("ID" AUTOINCREMENT)
            )''')

            logging.info("Create Database")
            return True
        except:
            logging.info("ERROR : Fail to CREATE TABLE DONATION")
            return None


# Donate item from user
def donate_item(type_item, item, detail, amount, donator_name, location, contact):
    try:
        # Set status to available
        status = "Available"

        # Set date donation format : dd/mm/yyyy
        date = datetime.date.today()
        date_format = date.strftime("%d/%m/%Y")
        
        # collect to list for insert into database
        all_values = [type_item, item, detail, amount, donator_name, date_format, location, contact, status]
        cur.execute('INSERT INTO Donation ("TypeItem" , "Item", "Detail", "Amount","DonatorName", "DateDonation", "Location", "Contact","Status") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', all_values)
        con.commit()
        logging.info(f"Add Item : {type_item}, {item}, {amount}, {donator_name}, {location}, {contact}")
        return True
    except:
        logging.info(f"ERROR : Add Item {type_item}, {item}, {donator_name}")
        return None


# Set status to check out item donate
def set_check_out(ID):
    try:
        cur.execute('UPDATE Donation SET Status = "Check out" WHERE ID = ?', (ID))
        con.commit()
        logging.info(f"Check out : {ID}")
        return True
    except:
        logging.info(f"ERROR : Fail to Check out {ID}")
        return False


# Sql to to list
def get_data(typeitem="-", location="-"):
    if typeitem == "-" and location == "-" :
        cur.execute("SELECT ID, TypeItem, Item, Detail, Amount, Location, Status FROM Donation WHERE Status = 'Available'")
    elif typeitem == "-" and location in PROVINCES:
        cur.execute("SELECT ID, TypeItem, Item, Detail, Amount, Location, Status FROM Donation WHERE Status = 'Available' AND Location = ?", (location,))
    elif typeitem in ITEM_TYPE and location == "-":
        cur.execute("SELECT ID, TypeItem, Item, Detail, Amount, Location, Status FROM Donation WHERE Status = 'Available' AND TypeItem = ?", (typeitem,))
    elif typeitem in ITEM_TYPE and location in PROVINCES:
        values = [typeitem, location]
        cur.execute("SELECT ID, TypeItem, Item, Detail, Amount, Location, Status FROM Donation WHERE Status = 'Available' AND TypeItem = ? AND Location = ?", (values))
    data = cur.fetchall()
    if data == []:
        data = [("-", "-", "-", "-", "-", "-", "-")]
    return data

# Sql to to list2
def get_all_data(ID):
    cur.execute("SELECT ID, TypeItem, Item, Detail, Amount, DonatorName, Location, Contact FROM Donation WHERE Status = 'Available' AND ID = ?", (ID,))
    data = cur.fetchall()
    return data

# Function Email
# Sent email to Donator
def sent_email(id, contact):
    # set up gmail
    app_gmail = ""
    app_pass = ""

    # format email
    data = get_all_data(id)
    name_donator = data[0][5]
    typeItem = data[0][1]
    Item = data[0][2]
    Detail = data[0][3]
    Amount = data[0][4]
    Location = data[0][6]
    donation_gmail = data[0][7]
    
    subject = f"จาก Hand2Hand Donation มีผู้สนใจสิ่งของที่คุณบริจาค ID : {id}"
    body = f'''คุณ {name_donator} 
    ID ของบริจาค : {id} 
    ประเภทสิ่งของ : {typeItem}
    สิ่งของ : {Item}
    รายละเอียด : {Detail}
    จำนวน : {Amount}
    จังหวัด : {Location} 
    มีผู้ที่สนใจในสิ่งของบริจาคของคุณ โปรดติดต่อ {contact} เพื่อทำการพูดคุยแลกเปลี่ยน'''

    msg = MIMEMultipart()
    msg["From"] = app_gmail
    msg["To"] = donation_gmail
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(app_gmail, app_pass)
        text = msg.as_string()

        # Sent Gmail
        server.sendmail(app_gmail, donation_gmail, text)
        logging.info(f"Sent Email to {donation_gmail}, {id}")
        return True

    except Exception as e:
        logging.info(f"ERROR : Fail to sent Email : {e}")
        return False

    finally:
        server.quit()


# Function UI
# Donation Page
def donate_ui():

    def donate():
        typeitem = get_typeitem.get()
        name = name_entry.get()
        detail = detail_entry.get()
        amount = amount_entry.get()
        donator_name = donatorName_entry.get()
        province = get_provinces.get()
        contact = contact_entry.get()

        try :
            amount = int(amount)
            
            if typeitem in ITEM_TYPE and province in PROVINCES and type(amount) == int and name != "" and detail != "" and donator_name != "" and "@gmail.com" in contact:
                
                donate_item(type_item=typeitem, item=name, detail=detail, amount=amount, donator_name=donator_name, location=province, contact=contact)

                # Clear data
                name_entry.delete(0, END)
                detail_entry.delete(0, END)
                amount_entry.delete(0, END)
                donatorName_entry.delete(0, END)
                contact_entry.delete(0, END)
                get_typeitem.set("เลือกประเภทสิ่งของ")
                get_provinces.set("เลือกจังหวัด")

                messagebox.showinfo(title="บริจาคเสร็จสิ้น", message="ขอบคุณสำหรับการบริจาค")
            else:
                messagebox.showinfo(title="กรอกข้อมูลไม่ถูกต้อง", message="กรุณากรอกข้อมูลให้ถูกต้องและลองใหม่อีกครั้ง")
        except:
            messagebox.showinfo(title="กรอกข้อมูลไม่ถูกต้อง", message="กรุณากรอกจำนวนเป็นตัวเลขเท่านั้น เช่น 2")

    view_donate = Tk()
    view_donate.title("Hand2Hand Donation")
    view_donate.geometry("500x320")
    view_donate.grid_columnconfigure((0, 1), weight=1)

    title = Label(view_donate, text="บริจาคสิ่งของ")
    title.config(font=FONT_TITLE)
    title.grid(row=1, column=0, sticky="")
    title2 = Label(view_donate, text="Hand2Hand")
    title2.config(font=FONT_TITLE)
    title2.grid(row=1, column=1, sticky="")

    # Text
    text_1 = Label(view_donate, text="ประเภทสิ่งของที่บริจาค", font=FONT_THAI_10_BOLD)
    text_2 = Label(view_donate, text="สินค้าที่บริจาค", font=FONT_THAI_10_BOLD)
    text_3 = Label(view_donate, text="รายละเอียดสินค้า", font=FONT_THAI_10_BOLD)
    text_4 = Label(view_donate, text="จำนวนสินค้าที่บริจาค", font=FONT_THAI_10_BOLD)
    text_5 = Label(view_donate, text="ชื่อผู้บริจาค", font=FONT_THAI_10_BOLD)
    text_6 = Label(view_donate, text="จังหวัด", font=FONT_THAI_10_BOLD)
    text_7 = Label(view_donate, text="Gmail", font=FONT_THAI_10_BOLD)

    # Entry box
    get_typeitem = ttk.Combobox(view_donate, values=ITEM_TYPE[1:], state='readonly',font=FONT_THAI_10)
    get_typeitem.set("เลือกประเภทสิ่งของ")
    name_entry = Entry(view_donate, font=FONT_THAI_10)
    detail_entry = Entry(view_donate, font=FONT_THAI_10)
    amount_entry = Entry(view_donate, font=FONT_THAI_10)
    donatorName_entry = Entry(view_donate, font=FONT_THAI_10)
    get_provinces = ttk.Combobox(view_donate, values=PROVINCES[1:], state='readonly',font=FONT_THAI_10)
    get_provinces.set("เลือกจังหวัด")
    contact_entry = Entry(view_donate, font=FONT_THAI_10)

    # Button
    bt_donate_item = Button(view_donate, text="บริจาคสิ่งของ", command=donate, font=FONT_THAI)

    # Layout Grid
    text_1.grid(row=3, column=0, pady=5)
    get_typeitem.grid(row=3, column=1, sticky="ew", pady=5)
    text_2.grid(row=4, column=0, pady=5)
    name_entry.grid(row=4, column=1, sticky="ew", pady=5)
    text_3.grid(row=5, column=0, pady=5)
    detail_entry.grid(row=5, column=1, sticky="ew", pady=5)
    text_4.grid(row=6, column=0, pady=5)
    amount_entry.grid(row=6, column=1, sticky="ew", pady=5)
    text_5.grid(row=7, column=0, pady=5)
    donatorName_entry.grid(row=7, column=1, sticky="ew", pady=5)
    text_6.grid(row=8, column=0, pady=5)
    get_provinces.grid(row=8, column=1, sticky="ew", pady=5)
    text_7.grid(row=9, column=0, pady=5)
    contact_entry.grid(row=9, column=1, sticky="ew", pady=5)
    bt_donate_item.grid(row=10, column=1, sticky="s", pady=5)

    view_donate.mainloop()


# List Page
def view_ui():

    # Set Up Columns
    columns = ["ID", "ประเภทสิ่งของ", "สิ่งของ", "รายละเอียด", "จำนวน", "สถานที่", "สถานะ"]
    columns_width = [5, 10, 10, 30, 5, 10, 10]

    # Function Display Row
    def display_row():
        # Clear Only Row
        [widget.destroy() for widget in second_frame.winfo_children() if isinstance(widget, Entry)]

        # Get data from dropdown
        typeitem_filter = dropdown_typeitem.get()
        provinces_filter = dropdown_provinces.get()

        data = get_data(typeitem=typeitem_filter, location=provinces_filter)


        for row_index, detail in enumerate(data):
            for col_index, value in enumerate(detail):
                entry = Entry(second_frame, width=columns_width[col_index], disabledforeground="black")
                entry.config(font=FONT_THAI_DATA)
                entry.grid(row=row_index + 1, column=col_index)
                entry.insert(0, str(value))
                entry.configure(state="disabled")

        # IF data not found Display Messagebox
        if data == [("-", "-", "-", "-", "-", "-", "-")]:
            messagebox.showinfo(title="ไม่พบสิ่งของ", message="ไม่พบสิ่งของ กรุณาลองใหม่อีกครั้ง")
            

    view_window = Tk()
    view_window.title("Hand2Hand List")
    view_window.geometry("960x800")

    # title
    main_title = Label(view_window, text="รายชื่อสิ่งของที่บริจาค")
    main_title.config(font=FONT_TITLE)
    main_title.pack(pady=20)

    # Dropdown filter
    dropdown_typeitem = ttk.Combobox(view_window, values=ITEM_TYPE, state='readonly')
    dropdown_typeitem.pack(pady=5)
    dropdown_typeitem.set("-")
    dropdown_provinces = ttk.Combobox(view_window, values=PROVINCES, state='readonly')
    dropdown_provinces.pack(pady=5)
    dropdown_provinces.set("-")


    # search
    bt_search = Button(view_window, text="ค้นหา", command=display_row)
    bt_search.config(font=FONT_THAI)
    bt_search.pack(pady=10)

    # Main Frame & Second Frame & Scrollbar
    main_frame = Frame(view_window)
    main_frame.pack(fill=BOTH, expand=1)

    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    my_canvas.configure(yscrollcommand=scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    second_frame = Frame(my_canvas, width=10, highlightbackground="black", highlightthickness=2)
    my_canvas.create_window((0,0), window=second_frame, anchor="nw")

    # List of items from SQL By Func name 'get_data'
    data = get_data()

    # Display Columns
    for col_index, col_name in enumerate(columns):
        label = Label(second_frame, text=col_name, padx=5, pady=5)
        label.config(font=FONT_THAI)
        label.grid(row=0, column=col_index)
    # Display Default Row
    for row_index, detail in enumerate(data):
        for col_index, value in enumerate(detail):
            entry = Entry(second_frame, width=columns_width[col_index], disabledforeground="black")
            entry.config(font=FONT_THAI_DATA)
            entry.grid(row=row_index + 1, column=col_index)
            entry.insert(0, str(value))
            entry.configure(state="disabled")


    view_window.mainloop()

# Checkout Page
def checkout_ui():

    # Checkout button function
    def checkout():
        id = id_entry.get()
        contact_checkout = contact_entry.get()

        if "@gmail.com" in contact_checkout:
                
            sent_email(id, contact_checkout)
            # Set to Check Out
            set_check_out(id)

            messagebox.showinfo(title="รับสิ่งของบริจาคแล้ว", message="ระบบจะติดต่อกับผู้บริจาค")
  
            # Clear data
            id_entry.delete(0, END)
            contact_entry.delete(0, END)
            id_entry.set("-")
        else:
            messagebox.showinfo(title="กรอกข้อมูลไม่ถูกต้อง", message="กรุณากรอกข้อมูลให้ถูกต้องและลองใหม่อีกครั้ง")


    # get ID from SQL
    cur.execute("SELECT ID FROM Donation WHERE Status = 'Available'")
    data = cur.fetchall()
    list_data = [item[0] for item in data]

    checkout_window = Tk()
    checkout_window.title("Hand2Hand CheckOut")
    checkout_window.geometry("320x170")

    # Title
    title = Label(checkout_window, text="รับของบริจาค", font=FONT_TITLE)
    title2 = Label(checkout_window, text="Hand2Hand", font=FONT_TITLE)

    # Text box
    text_1 = Label(checkout_window, text="ID ที่ต้องการรับของบริจาค", font=FONT_THAI_10_BOLD)
    text_2 = Label(checkout_window, text="Gmail ผู้รับบริจาค", font=FONT_THAI_10_BOLD)

    # Entry box
    id_entry = ttk.Combobox(checkout_window, values=list_data, state='readonly', font=FONT_THAI_10)
    id_entry.set("-")
    contact_entry = Entry(checkout_window, font=FONT_THAI_10)

    # Button
    bt_checkout_item = Button(checkout_window, text="รับสิ่งของบริจาค", command=checkout, font=FONT_THAI)

    # Layout Grid
    title.grid(row=1, column=0, sticky="")
    title2.grid(row=1, column=1, sticky="")
    text_1.grid(row=3, column=0, pady=5)
    id_entry.grid(row=3, column=1, sticky="ew", pady=5)
    text_2.grid(row=4, column=0, pady=5)
    contact_entry.grid(row=4, column=1, sticky="ew", pady=5)
    bt_checkout_item.grid(row=5, column=1, sticky="s", pady=5)


    checkout_window.mainloop()

# Main Program
if __name__ == "__main__":

    create_table()

    # Main UI
    main_ui = Tk()
    main_ui.title("Hand2Hand Program")
    main_ui.geometry("400x400")

    main_title = Label(main_ui, text="Donation Hub Program")
    main_title.config(font=FONT_TITLE)
    main_title.pack(pady=10)

    main_title2 = Label(main_ui, text="Hand2Hand")
    main_title2.config(font=FONT_TITLE)
    main_title2.pack(pady=10)

    bt_go_donate = Button(main_ui, text="บริจาคสิ่งของ", command=donate_ui)
    bt_go_donate.config(font=FONT_THAI)
    bt_go_donate.pack(pady=30)

    bt_go_checkout = Button(main_ui, text="ดูรายการของบริจาค", command=view_ui)
    bt_go_checkout.config(font=FONT_THAI)
    bt_go_checkout.pack(pady=30)

    bt_go_view = Button(main_ui, text="รับของบริจาค", command=checkout_ui)
    bt_go_view.config(font=FONT_THAI)
    bt_go_view.pack(pady=30)

    main_ui.mainloop()