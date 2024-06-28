# Capstone_Price_Negotiator_Bot

### Project Description: 
This project makes use of a chatbot system that can negotiate the price of various products. The chatbot
allows user's to communicate and bargain while browsing items on the site, simulating a real world commerce interaction.

Data Source: ... 
 
## Changelog
### May, 29. 2024 - Justin
### Frontend Skeleton
+ Implemented a simple skeleton build for our front-end deployment
+ Added very basic core interactions such as Navbars, buttons, links
+ Created a simple CSS style schema
+ Started on some of the core scripting logic within our script.js

### June, 01. 2024 - Justin
### Account Management Backend
+ Implemented a backend server for the webapp that handles simple account creation.
+ Created a .JSON file that stores encrypted account details
+ Integrated simple Login functionality for accounts that have been saved to our .JSON file.
+ Various Front-End tweaks

## June, 03. 2024 - Batool
+ Implemented the first, very simple text-based chatbot with pre-defined responses 

## June, 10. 2024 - Justin
### Negotiating From Checkout
- Removed the option to negotiate on an item-by-item basis 
+ Added a simple checkout system as well as adding items to a user's 'cart'
+ Changed the system for dynamically adding products/HTML elements

## June, 28. 2024 - Justin
### Added Branch: MVP_Basic_Feature_Merging
### MVP: Chatbot Integration, Checkout Page
+ Added a Cart system and 'Checkout' page that allows the user to add products to their virtual cart, receive a total, and negotiate/purchase the items.
+ Added chatbot functionality to the new 'Checkout' page.
+ Added a working NavBar to make site navigation more seamless and visible.
- Commented out the previous 'add to cart' button as it caused bugs/crashed related to the Database.

## June, 28. 2024 - Justin
### Working on Branch: MVP_Basic_Feature_Merging
### MVP: Chatbot Logging, Chatbot Log Resetting, NavBar Account Display
+ Added a chatlog for the Chatbot section so you can see the conversation history.
+ Added a function to reset the chatlog when refreshing the page to avoid clutter / old messages
+ Added a greeting and user email display to the navbar to show if you are logged in & under which account.
