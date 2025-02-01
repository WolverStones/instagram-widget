# 📸 Instagram Feed Widget

**Author**: [Patrik Müller](https://github.com/WolverStones)  
**License**: Apache-2.0  
**Repository**: [GitHub](https://github.com/WolverStones)  

## 🎯 Project Description
This **Instagram Feed Widget** allows you to display the latest posts from a specific Instagram account. The widget dynamically fetches data from the API and displays **photos and videos**, which can be clicked to open on Instagram.

## ✨ Features
✔ **Dynamic profile loading** – name, username, number of posts, and followers  
✔ **Instagram feed display** – images and videos  
✔ **Automatic redirection to Instagram** when clicked  
✔ **Responsive design** – displays posts in a **grid layout**  

## 🔧 Installation & Usage
1️⃣ **Download or clone this repository**  
2️⃣ **Run an API server (Flask, FastAPI, or any backend that provides data from the Instagram API)**  
3️⃣ **Update the API URL in `loadInstagramData()`**  
4️⃣ **Add the widget to your webpage**:

```html
<div id="instagram-widget"></div>
<script src="https://yourserver.com/instagram_widget.js"></script>
```

## 🔗 API Endpoint
- **GET `/feed`** – Returns a list of recent posts  
- **JSON response** includes `media_url`, `media_type`, `permalink`, etc.

## 📜 License
This project is licensed under **Apache-2.0**. You are free to **use, modify, and distribute** it, but you must **credit the author** and keep the original license.

---

If you have any questions or suggestions for improvements, feel free to open an issue or pull request! 🚀

