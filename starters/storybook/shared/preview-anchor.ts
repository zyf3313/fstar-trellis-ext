export const reviewAnchorQueryParam = 'reviewAnchor'
export const reviewTargetQueryParam = 'reviewTarget'

type LocationReader = Pick<Location, 'search'>
type AnchorDocument = Pick<Document, 'getElementById'>
type FrameScheduler = (callback: FrameRequestCallback) => number
type QueryWriter = (search: string) => void

type ScrollOptions = {
  parentLocation?: LocationReader
  documentRef?: AnchorDocument
  schedule?: FrameScheduler
  replaceParentSearch?: QueryWriter
}

export function readReviewAnchor(parentLocation: LocationReader): string | undefined {
  try {
    const query = new URLSearchParams(parentLocation.search)
    const anchor = query.get(reviewAnchorQueryParam)
    const target = query.get(reviewTargetQueryParam)
    const currentPath = query.get('path')
    return anchor
      && /^[A-Za-z0-9_-]+$/.test(anchor)
      && target
      && target === currentPath
      && /^\/story\/[a-z0-9]+(?:-[a-z0-9]+)*--document$/.test(target)
      ? anchor
      : undefined
  } catch {
    return undefined
  }
}

export function scrollToReviewAnchor({
  parentLocation = window.parent.location,
  documentRef = document,
  schedule = requestAnimationFrame,
  replaceParentSearch = replaceWindowParentSearch,
}: ScrollOptions = {}): boolean {
  const anchor = readReviewAnchor(parentLocation)
  if (!anchor) return false

  const nextSearch = new URLSearchParams(parentLocation.search)
  nextSearch.delete(reviewAnchorQueryParam)
  nextSearch.delete(reviewTargetQueryParam)
  replaceParentSearch(nextSearch.toString())
  schedule(() => {
    documentRef.getElementById(anchor)?.scrollIntoView({ block: 'start' })
  })
  return true
}

function replaceWindowParentSearch(search: string): void {
  try {
    const parentUrl = new URL(window.parent.location.href)
    parentUrl.search = search
    window.parent.history.replaceState(window.parent.history.state, '', parentUrl)
  } catch {
    // The anchor remains safe to use even when a cross-origin parent cannot be updated.
  }
}
