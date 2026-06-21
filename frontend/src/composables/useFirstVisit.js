import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const STORAGE_KEY = 'np-visited-pages'

function getVisitedPages() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function markVisited(path) {
  const pages = getVisitedPages()
  if (!pages.includes(path)) {
    pages.push(path)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(pages))
  }
}

export function useFirstVisit() {
  const route = useRoute()
  const isFirstVisit = ref(false)
  const transitionName = ref('')

  watch(
    () => route.path,
    (path) => {
      const visited = getVisitedPages()
      if (!visited.includes(path)) {
        isFirstVisit.value = true
        transitionName.value = 'page-slide-fade'
      } else {
        isFirstVisit.value = false
        transitionName.value = ''
      }
    },
    { immediate: true }
  )

  function onAfterEnter() {
    if (isFirstVisit.value) {
      markVisited(route.path)
    }
  }

  return { isFirstVisit, transitionName, onAfterEnter }
}
