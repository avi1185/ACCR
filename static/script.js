function vote(complaintId) {
  fetch(`/vote/${complaintId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .then((data) => {
      let voteCell = document.querySelector(`.votes[data-id="${complaintId}"]`);
      let statusCell = document.querySelector(
        `.status[data-id="${complaintId}"]`
      );
      voteCell.textContent = data.votes;
      statusCell.textContent = data.status;
      statusCell.setAttribute("data-status", data.status);
    });
}
