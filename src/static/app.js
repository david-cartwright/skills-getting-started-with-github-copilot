document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> <span class="availability-count">${spotsLeft}</span> spots left</p>
        `;

        // Participants section (unstyled list with delete buttons)
        const participantsTitle = document.createElement('p');
        participantsTitle.className = 'participants-title';
        participantsTitle.textContent = 'Participants:';
        activityCard.appendChild(participantsTitle);

        const participantsListEl = document.createElement('ul');
        participantsListEl.className = 'participants-list';

        if (details.participants && details.participants.length > 0) {
          details.participants.forEach(participant => {
            const li = document.createElement('li');
            li.className = 'participant-item';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'participant-name';
            nameSpan.textContent = participant;

            const delBtn = document.createElement('button');
            delBtn.className = 'delete-participant';
            delBtn.setAttribute('aria-label', `Remove ${participant}`);
            delBtn.dataset.activity = name;
            delBtn.dataset.email = participant;
            delBtn.textContent = '✖';

            li.appendChild(nameSpan);
            li.appendChild(delBtn);

            participantsListEl.appendChild(li);
          });
        } else {
          const li = document.createElement('li');
          li.className = 'participant-item no-participants';
          li.textContent = 'No participants yet';
          participantsListEl.appendChild(li);
        }

        activityCard.appendChild(participantsListEl);

        activitiesList.appendChild(activityCard);

        // Attach delete handler (event delegation)
        participantsListEl.addEventListener('click', async (e) => {
          if (!e.target.classList.contains('delete-participant')) return;

          const activityName = e.target.dataset.activity;
          const email = e.target.dataset.email;

          try {
            const resp = await fetch(`/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`, {
              method: 'DELETE',
            });

            const resJson = await resp.json();

            if (resp.ok) {
              // Refresh activities to keep UI in sync
              fetchActivities();

              // show a short info message
              messageDiv.textContent = resJson.message || 'Removed participant';
              messageDiv.className = 'info';
              messageDiv.classList.remove('hidden');
              setTimeout(() => messageDiv.classList.add('hidden'), 3000);
            } else {
              messageDiv.textContent = resJson.detail || 'Failed to remove participant';
              messageDiv.className = 'error';
              messageDiv.classList.remove('hidden');
              setTimeout(() => messageDiv.classList.add('hidden'), 5000);
            }
          } catch (err) {
            console.error('Error removing participant:', err);
            messageDiv.textContent = 'Failed to remove participant. Try again.';
            messageDiv.className = 'error';
            messageDiv.classList.remove('hidden');
            setTimeout(() => messageDiv.classList.add('hidden'), 5000);
          }
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show new participant immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
