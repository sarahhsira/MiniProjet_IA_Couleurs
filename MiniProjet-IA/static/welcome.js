document.addEventListener("DOMContentLoaded", () => {
  // Désactiver le défilement
  document.body.style.overflow = "hidden"

  // Empêcher le défilement par la molette de la souris
  window.addEventListener("wheel", preventScroll, { passive: false })

  // Empêcher le défilement par les touches du clavier
  window.addEventListener("keydown", preventScrollKeys, { passive: false })

  // Empêcher le défilement par le toucher sur mobile
  window.addEventListener("touchmove", preventScroll, { passive: false })

  function preventScroll(e) {
    e.preventDefault()
  }

  function preventScrollKeys(e) {
    // Touches de défilement: flèches, espace, page up/down, home, end
    const keys = [32, 33, 34, 35, 36, 37, 38, 39, 40]
    if (keys.includes(e.keyCode)) {
      e.preventDefault()
      return false
    }
  }

  // Animation pour le bouton CTA
  const ctaButton = document.getElementById("startButton")

ctaButton.addEventListener("click", () => {
  // Redirection vers index.html
  window.location.href = 'index.html';
});


  // Effet de survol amélioré pour les cartes
  const features = document.querySelectorAll(".feature")

  features.forEach((feature) => {
    feature.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px)"
      this.style.boxShadow = "0 8px 20px rgba(0, 0, 0, 0.3), 0 0 15px rgba(212, 175, 55, 0.3)"
      this.style.borderColor = "rgba(212, 175, 55, 0.3)"

      const icon = this.querySelector(".feature-icon i")
      icon.style.transform = "scale(1.2)"
      icon.style.transition = "transform 0.3s ease"
    })

    feature.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)"
      this.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.2)"
      this.style.borderColor = "rgba(212, 175, 55, 0.2)"

      const icon = this.querySelector(".feature-icon i")
      icon.style.transform = "scale(1)"
    })
  })

  // Ajouter un effet de brillance au bouton
  function addButtonGlow() {
    const button = document.querySelector(".cta-button")
    let glowIntensity = 0
    let increasing = true

    setInterval(() => {
      if (increasing) {
        glowIntensity += 0.05
        if (glowIntensity >= 1) {
          increasing = false
        }
      } else {
        glowIntensity -= 0.05
        if (glowIntensity <= 0.3) {
          increasing = true
        }
      }

      button.style.boxShadow = `0 4px 10px rgba(0, 0, 0, 0.2), 0 0 ${15 + glowIntensity * 10}px rgba(212, 175, 55, ${0.3 + glowIntensity * 0.2})`
    }, 50)
  }

  // Optimiser la mise en page
  function optimizeLayout() {
    const vh = window.innerHeight
    const container = document.querySelector(".container")
    const header = document.querySelector("header")
    const mainContent = document.querySelector(".main-content")
    const ctaSection = document.querySelector(".cta-section")
    const footer = document.querySelector("footer")

    // Calculer les hauteurs
    const headerHeight = header.offsetHeight
    const footerHeight = footer.offsetHeight
    const ctaHeight = ctaSection.offsetHeight

    // Calculer l'espace disponible pour le contenu principal
    const availableHeight = vh - headerHeight - footerHeight - ctaHeight - 80 // Marges

    // Définir une hauteur minimale pour les cartes
    const minCardHeight = 250
    const maxCardHeight = 350

    // Ajuster la hauteur des cartes
    const featuresContainer = document.querySelector(".features")
    const cardHeight = Math.min(Math.max(availableHeight, minCardHeight), maxCardHeight)
    featuresContainer.style.height = `${cardHeight}px`

    // Ajuster les marges pour centrer verticalement
    const remainingSpace = vh - (headerHeight + cardHeight + ctaHeight + footerHeight)
    if (remainingSpace > 0) {
      const topMargin = remainingSpace * 0.3 // 30% en haut
      const bottomMargin = remainingSpace * 0.7 // 70% en bas

      mainContent.style.marginBottom = `${bottomMargin / 2}px`
      ctaSection.style.marginBottom = `${bottomMargin / 2}px`
    }
  }

  // Exécuter au chargement et au redimensionnement
  window.addEventListener("load", () => {
    addButtonGlow()
    setTimeout(optimizeLayout, 100) // Délai pour laisser les animations se terminer
  })
  window.addEventListener("resize", optimizeLayout)
})
