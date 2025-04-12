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
  
});