function getCourseId() {
  return new URLSearchParams(location.search).get('course') || '11';
}

function goBackToCourse() {
  const course = getCourseId();
  location.href = `/course/classroom.html?course=${course}`;
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-action="back"]').forEach((btn) => {
    btn.addEventListener('click', goBackToCourse);
  });
});
