import { config } from '@vue/test-utils'

// Mock FontAwesome globalement pour les tests
config.global.stubs = {
  'font-awesome-icon': {
    template: '<i class="fa-mock" />'
  }
}

// Mock des fonctions CSS et animations
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
