import { mount } from '@vue/test-utils'
import JdrSpinner from '@/components/JdrSpinner.vue'

describe('JdrSpinner', () => {
  it('affiche le spinner avec le label', () => {
    const wrapper = mount(JdrSpinner, {
      props: { label: 'Chargement...' }
    })
    expect(wrapper.text()).toContain('Chargement...')
    expect(wrapper.find('.jdr-spinner').exists()).toBe(true)
  })

  it('accepte les props size et border', () => {
    const wrapper = mount(JdrSpinner, {
      props: { size: 64, border: 8 }
    })
    const spinner = wrapper.find('.jdr-spinner')
    expect(spinner.attributes('style')).toContain('width: 64px')
    expect(spinner.attributes('style')).toContain('border-width: 8px')
  })
})
