document.addEventListener('DOMContentLoaded', function() {
  // Like Button
  document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', async function() {
      const postId = this.getAttribute('data-post-id');
      console.log('Liking post:', postId);

      try {
        const response = await fetch('/like', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ post_id: postId }),
          credentials: 'include',
        });

        if (response.status === 401) {
          const data = await response.json();
          if (data.redirect) {
            window.location.href = data.redirect; // Force redirect to login
            return;
          }
        }

        if (!response.ok) {
          throw new Error('Failed to like post');
        }

        const data = await response.json();
        console.log('Like success:', data);
        // Optional: Update UI (e.g., change button color)
      } catch (error) {
        console.error('Error:', error);
      }
    });
  });

  // Dislike Button (similar logic)
  document.querySelectorAll('.dislike-button').forEach(button => {
    button.addEventListener('click', async function() {
      const postId = this.getAttribute('data-post-id');
      console.log('Disliking post:', postId);

      try {
        const response = await fetch('/dislike', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ post_id: postId }),
          credentials: 'include',
        });

        if (response.status === 401) {
          const data = await response.json();
          if (data.redirect) {
            window.location.href = data.redirect; // Force redirect to login
            return;
          }
        }

        if (!response.ok) {
          throw new Error('Failed to dislike post');
        }

        const data = await response.json();
        console.log('Dislike success:', data);
        // Optional: Update UI
      } catch (error) {
        console.error('Error:', error);
      }
    });
  });
});