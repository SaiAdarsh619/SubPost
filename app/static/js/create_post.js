document.addEventListener('DOMContentLoaded', function () {
  const post_body = document.getElementById('post_body');

  // 📋 Paste Handler
  post_body.addEventListener('paste', function (e) {
    for (const item of e.clipboardData.items) {
      if (item.type.indexOf("image") !== -1) {
        const file = item.getAsFile();
        const reader = new FileReader();
        reader.onload = function (event) {
          const img = document.createElement("img");
          img.src = event.target.result;

          const wrapper = document.createElement("div");
          wrapper.appendChild(img);
          post_body.appendChild(wrapper);
        };
        reader.readAsDataURL(file);
        e.preventDefault();
      }
    }
  });

  // 🖱️ Drag & Drop Handler
  post_body.addEventListener('dragover', function (e) {
    e.preventDefault();
  });

  post_body.addEventListener('drop', function (e) {
    e.preventDefault();
    const files = e.dataTransfer.files;
    for (const file of files) {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const img = document.createElement("img");
          img.src = event.target.result;

          const wrapper = document.createElement("div");
          wrapper.appendChild(img);
          post_body.appendChild(wrapper);
        };
        reader.readAsDataURL(file);
      }
    }
  });

  // 💾 Save Handler
  document.getElementById('postBtn').addEventListener('click', function (event) {
    event.preventDefault(); // ✅ Prevent default form behavior
  
    const btn = document.getElementById('postBtn');
    const originalContent = btn.innerHTML;
  
    const spinner = `<span class="spinner" style="
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid white;
      border-top: 2px solid transparent;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    "></span>`;
  
    btn.disabled = true;
    btn.innerHTML = spinner;
  
    const content = post_body.innerHTML;
    const title = document.getElementById('post_title').value.trim();
  
    if (!title || !content) {
      alert('Please fill in both title and content!');
      btn.innerHTML = originalContent;
      btn.disabled = false;
      return;
    }
  
    fetch('/create_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title, content: content })
    })
      .then(res => res.json())
      .then(data => {
        const statusElement = document.getElementById('status');
        if (data.success) {
          statusElement.textContent = '✅ Post published successfully!';
          statusElement.style.color = 'green';
        } else {
          statusElement.textContent = '❌ Failed to publish post.';
          statusElement.style.color = 'red';
        }
      })
      .catch(err => {
        const statusElement = document.getElementById('status');
        statusElement.textContent = '❌ An error occurred while publishing the post.';
        statusElement.style.color = 'red';
        console.error(err);
      })
      .finally(() => {
        // ✅ Restore the button no matter what
        btn.innerHTML = originalContent;
        btn.disabled = false;
      });
  });
  
  const userData = document.getElementById('user-data');
  const username = userData?.dataset.username;

  if(username != 'None') {
    console.log(username)
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
          <a href="/your_post" style="display: block; padding: 10px;">Your Post</a>        
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
    }
    else{
      // User not logged in – show login and signup buttons
      document.querySelector('.nav-right').innerHTML = `
        <a href="/login" class='login_button' >Login</a>
        <a href="/signup" class = 'signup_button' >Signup</a>
      `;
    }


});