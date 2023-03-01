## The site was created as part of the 100 Days of Code: The Complete Python Pro Bootcamp course, slightly modified to my liking and deployed on the railway.app

### Some website presentation from the course:
<a href="https://gifyu.com/image/S7dzE"><img src="https://s3.gifyu.com/images/Sheety-Blog.gif" alt="Sheety-Blog.gif" border="0" /></a>

<p>This is a Python code for a Flask web application that can be used to create a blog website. The application provides various functionalities for the users such as registering an account, logging in, logging out, creating, editing, and deleting blog posts, and adding comments on blog posts.</p>
<p>Here is a more detailed breakdown of the code:</p>
<p><strong>Import Statements and Configuration Details:</strong></p>
<p>The first part of the code includes the import statements and configuration details for the Flask application. It imports the Flask class, SQLAlchemy, CKEditor, Bootstrap, LoginManager, Gravatar, and several forms to handle user input. It also includes the configuration details such as the database URL, secret key, and debug settings.</p>
<p><strong>Database Schema:</strong></p>
<p>The second part of the code defines the database schema using SQLAlchemy. It includes three tables: "users", "blog_posts", and "comments". The "users" table contains user information such as id, email, password, and name. The "blog_posts" table contains information about the blog posts such as title, subtitle, body, and author. The "comments" table contains comments on the blog posts and stores the text of the comment, the date, and the commenter's id.</p>
<p><strong>Routes:</strong></p>
<p>The next part of the code includes several decorators for the routes of the Flask application.</p>
<ul>
 <li>The "/" route is for the home page and displays all the blog posts.</li>
 <li>The "/about" route displays information about the website.</li>
 <li>The "/contact" route handles user messages and sends an email notification to the recipient.</li>
 <li>The "/post/int:post_id" route displays a particular blog post and allows users to add comments to the post.</li>
 <li>The "/delete/int:post_id" route deletes a blog post.</li>
 <li>The "/new-post" route creates a new blog post.</li>
 <li>The "/edit-post/int:post_id" route allows users to edit an existing blog post.</li>
 <li>The "/register" route handles user registration.</li>
 <li>The "/login" route handles user login.</li>
 <li>The "/logout" route handles user logout.</li>
</ul>
<p><strong>Authorization:</strong></p>
<p>The "admin_only" and "login_required" decorators are used to handle user authorization. The "admin_only" decorator checks if the user is an admin, and if not, it returns a 403 Forbidden error. The "login_required" decorator checks if the user is logged in, and if not, it redirects the user to the login page.</p>
<p><strong>Login Manager and User Loader:</strong></p>
<p>The next part of the code defines the login manager and the user loader. The user loader is used to load the user object from the user ID stored in the session. It connects the abstract user that Flask Login uses with the actual users in the model.</p>
<p><strong>Registration and Database Creation:</strong></p>
<p>The final part of the code includes the registration of the application, and the creation of the database tables if they do not already exist. The application is then run on the local server.</p>
<p>Overall, this Flask web application provides a basic structure for a blog website with features such as user registration, login, and authorization, blog post creation, editing, and deletion, and commenting. It can be used as a starting point for building more complex web applications.</p>
