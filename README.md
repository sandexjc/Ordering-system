# Ordering system

# Preview

Login && Home
- The system is initially designed to be used only by private group of people which makes the login necessary.
- First account should be created by the terminal as superuser/admin in order to be able to login into the web interface and create additional accounts.
- Once logged in you will land on the home page where you will be able to find the nav bar with account settings, user management and home page button.
<img width="1400" alt="Login page" src="https://github.com/sandexjc/Ordering-system/assets/84847008/bf73fb52-2e78-4911-a59d-76b3b349d1b5">

<br><br>

Navigation
- Orders in the system are devided by internals and externals.(The feture is requested by the client).
- You can filter how many records to be displayed by selecting the Filter icon. Choices are 80, 100, 150 etc ... default is 80.
- You can search for specific order by ID, Client name, Telephone, or Date using the search button on the right.
<img width="1414" alt="Navigation" src="https://github.com/sandexjc/Ordering-system/assets/84847008/7698f25e-7069-460b-b900-907e8f732f99">

<br><br>

Order management
- Orders are sorted by Date in descending order. (requested by the client)
- Orders in the system are devided by internals and externals.
- Create new order button is right above the orders. Once clicked it will load new page where you will be able to fill the order form.
<img width="1414" alt="Create_order" src="https://github.com/sandexjc/Ordering-system/assets/84847008/40aa4104-00ca-4bac-a213-52ffeee277f9">

<br><br>

- Created orders can be edited at any time. You can add/remove additional items or change prices and quantity.
<img width="1414" alt="Edit_order" src="https://github.com/sandexjc/Ordering-system/assets/84847008/35f67f6c-2ebd-4501-b44b-86211567388e">

<br><br>

- Orders state can be easily managed by clicking on the update button. Modal window with predefined states will be opened and updating the state will not trigger page closure or reload due to usage of AJAX requests.
- One or more order items and states can be updated simultaneously.
<img width="1414" alt="update_order" src="https://github.com/sandexjc/Ordering-system/assets/84847008/d6999e3b-4792-4810-8026-5b32b4f0d8de">

<br><br>

- Orders can be deleted by clicking the delete button for the selected order.
- Modal window will be loaded to confirm the action.
<img width="1414" alt="delete_order" src="https://github.com/sandexjc/Ordering-system/assets/84847008/b7b8598b-8f65-44a8-9d61-524a08ab96c3">

<br><br>

- Order history can be viewed by clicking on the history button.
- Offcanvas tab will pop-up on the right of the screen with information about the latest changes for the selected order.
<img width="1414" alt="order_history" src="https://github.com/sandexjc/Ordering-system/assets/84847008/188ece8f-9e34-46c3-873e-a7e34fd948ed">

<br><br>

- Orders have quick print view by selecting the print button. (requested by the client)
<img width="1414" alt="print_order" src="https://github.com/sandexjc/Ordering-system/assets/84847008/fb490a42-411d-462b-b923-73a8772908a5">

