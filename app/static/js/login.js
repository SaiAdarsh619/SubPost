document.addEventListener('DOMContentLoaded', () => {

  async function login(event) {
    event.preventDefault();
    document.getElementById('submit').addAttribute('disabled');
    // Get the form data
    const loginform = document.getElementById('loginform');
    const formdata = new FormData(loginform);
    const jsondata = Object.fromEntries(formdata.entries());
    console.log(jsondata);

    const port = 5000;
    const domain = "domainc.ddns.net";
    const domainon = true;
    const url = domainon ? `http://${domain}:${port}/login` : `http://localhost:5000/login`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jsondata)
    }).then(response => {
      // if response contains redirection info
      if (response.redirected) {
        //redirect their
        window.location.href = response.url;
      }
    }).catch(error => console.error("Error : ", error));

    if (response.ok)
      console.log('login successfull');
    else
      console.log('login failed');
  }

  const userData = document.getElementById('user-data');
  const username = userData && Object.keys(userData.dataset).length > 0 ? userData.dataset.username : undefined;

  if (username !== "") {
    console.log(username);
      // User is logged in – show profile dropdown and create post button
    document.querySelector('.nav-right').innerHTML = `
      <a href="/create_post" class="create_post_button" id="create-post" style="display: inline-flex; align-items: center; margin-right: 10px;">
        <span class="flex items-center justify-center">
      <span class="flex mr-xs">
        <svg fill="currentColor" height="20" viewBox="0 0 20 20" width="20" xmlns="http://www.w3.org/2000/svg">
        <path d="M18 9.25h-7.25V2a.772.772 0 0 0-.75-.75.772.772 0 0 0-.75.75v7.25H2a.772.772 0 0 0-.75.75c0 .398.352.75.75.75h7.25V18c0 .398.352.75.75.75s.75-.352.75-.75v-7.25H18c.398 0 .75-.352.75-.75a.772.772 0 0 0-.75-.75Z"></path>
        </svg>
      </span>
      <span class="flex items-center gap-xs">Create</span>
        </span>
      </a>
      <div id="profileDropdownTrigger" style="display: inline-flex; align-items: center; cursor: pointer; margin-left: 10px;">
        <div class="profile-icon" style="
      background-color: #4a90e2;
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
        ">${username[0].toUpperCase()}</div>
        
      </div>
      <div id="profileDropdownMenu" class="dropdown-menu" style="
        display: none;
        position: absolute;
        top: 55px;
        right: 24px;
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 100;
      ">
        <a href="/profile" style="display: block; padding: 10px;">Profile</a>
        <a href="/settings" style="display: block; padding: 10px;">Settings</a>
        <a href="/logout" style="display: block; padding: 10px;">Logout</a>
      </div>
      `;

    // Add dropdown toggle logic
    const trigger = document.getElementById('profileDropdownTrigger');
    const menu = document.getElementById('profileDropdownMenu');
    trigger.addEventListener('click', () => {
      menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', function (e) {
      if (!trigger.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = 'none';
      }
    });
  } else {
    // User not logged in – show login and signup buttons
    const navRight = document.querySelector('.nav-right');
    if (navRight) {
      navRight.innerHTML = `
        <a href="/login" class='login_button' style="margin-right: 10px;">Login</a>
        <a href="/signup" class='signup_button' style="margin-left: 10px;">Signup</a>
      `;
    } else {
      console.error("Element with class 'nav-right' not found.");
    }
  }
});
