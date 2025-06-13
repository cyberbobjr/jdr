import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatMessage from '../../src/components/ChatMessage.vue'
import type { ConversationMessage, MessagePart, MessageUsage } from '../../src/core/interfaces'

describe('ChatMessage', () => {
  const mockMessagePart: MessagePart = {
    content: 'Test content',
    timestamp: '2025-01-15T10:30:00.000Z',
    part_kind: 'text'
  }

  const mockUsage: MessageUsage = {
    requests: 1,
    request_tokens: 10,
    response_tokens: 20,
    total_tokens: 30
  }

  const mockConversationMessage: ConversationMessage = {
    parts: [mockMessagePart],
    kind: 'response',
    usage: mockUsage,
    model_name: 'gpt-4o',
    timestamp: '2025-01-15T10:30:00.000Z'
  }

  it('renders a single message correctly', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        messages: [mockConversationMessage]
      }
    })

    expect(wrapper.find('.chat-message').exists()).toBe(true)
    expect(wrapper.find('.message-response').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test content')
  })

  it('shows debug info when showDebugInfo is true', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        messages: [mockConversationMessage],
        showDebugInfo: true
      }
    })

    expect(wrapper.find('.usage-details').exists()).toBe(true)
    expect(wrapper.text()).toContain('Requêtes: 1')
    expect(wrapper.text()).toContain('Total: 30')
  })

  it('hides debug info when showDebugInfo is false', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        messages: [mockConversationMessage],
        showDebugInfo: false
      }
    })

    expect(wrapper.find('.usage-details').exists()).toBe(false)
  })

  it('renders multiple message parts correctly', () => {
    const multiPartMessage: ConversationMessage = {
      parts: [
        {
          content: 'First part',
          timestamp: '2025-01-15T10:30:00.000Z',
          part_kind: 'user-prompt'
        },
        {
          content: 'Second part',
          timestamp: '2025-01-15T10:30:01.000Z',
          part_kind: 'tool-call'
        }
      ],
      kind: 'request',
      timestamp: '2025-01-15T10:30:00.000Z'
    }

    const wrapper = mount(ChatMessage, {
      props: {
        messages: [multiPartMessage],
        showDebugInfo: true // force affichage pour éviter le filtrage
      }
    })

    const parts = wrapper.findAll('.message-part')
    expect(parts).toHaveLength(2)
    expect(parts[0].classes()).toContain('part-user')
    expect(parts[1].classes()).toContain('part-tool-call')
  })

  it('renders tool-call content as code', () => {
    const toolCallMessage: ConversationMessage = {
      parts: [
        {
          content: '{"function": "test", "args": {"value": 42}}',
          timestamp: '2025-01-15T10:30:00.000Z',
          part_kind: 'tool-call'
        }
      ],
      kind: 'request',
      timestamp: '2025-01-15T10:30:00.000Z'
    }

    const wrapper = mount(ChatMessage, {
      props: {
        messages: [toolCallMessage],
        showDebugInfo: true // force affichage pour éviter le filtrage
      }
    })

    expect(wrapper.find('.code-content').exists()).toBe(true)
    expect(wrapper.find('.text-content').exists()).toBe(false)
  })

  it('renders text content with basic markdown', () => {
    const textMessage: ConversationMessage = {
      parts: [
        {
          content: 'This is **bold** and *italic* text',
          timestamp: '2025-01-15T10:30:00.000Z',
          part_kind: 'text'
        }
      ],
      kind: 'response',
      timestamp: '2025-01-15T10:30:00.000Z'
    }

    const wrapper = mount(ChatMessage, {
      props: {
        messages: [textMessage],
        showDebugInfo: true // force affichage pour éviter le filtrage
      }
    })

    const textContent = wrapper.find('.text-content')
    expect(textContent.exists()).toBe(true)
    // Le rendu markdown est <span class="jdr-bold"> pour bold et <em> pour italic
    expect(textContent.html()).toContain('<span class="jdr-bold">bold</span>')
    expect(textContent.html()).toContain('<em>italic</em>')
  })

  it('displays instructions when provided', () => {
    const messageWithInstructions: ConversationMessage = {
      parts: [mockMessagePart],
      instructions: 'Special instructions for this message',
      kind: 'request',
      timestamp: '2025-01-15T10:30:00.000Z'
    }

    const wrapper = mount(ChatMessage, {
      props: {
        messages: [messageWithInstructions]
      }
    })

    expect(wrapper.find('.message-instructions').exists()).toBe(true)
    expect(wrapper.text()).toContain('Special instructions for this message')
  })

  it('displays dynamic reference when provided', () => {
    const partWithDynamicRef: MessagePart = {
      content: 'Test content',
      timestamp: '2025-01-15T10:30:00.000Z',
      part_kind: 'text',
      dynamic_ref: 'character-123'
    }

    const messageWithDynamicRef: ConversationMessage = {
      parts: [partWithDynamicRef],
      kind: 'response',
      timestamp: '2025-01-15T10:30:00.000Z'
    }

    const wrapper = mount(ChatMessage, {
      props: {
        messages: [messageWithDynamicRef]
      }
    })

    expect(wrapper.find('.dynamic-ref').exists()).toBe(true)
    expect(wrapper.text()).toContain('character-123')
  })

  it('handles empty messages array', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        messages: []
      }
    })

    expect(wrapper.find('.chat-message').exists()).toBe(false)
  })

  it('applies correct CSS classes for different message kinds', () => {
    const testCases = [
      { kind: 'request', expectedClass: 'message-request' },
      { kind: 'response', expectedClass: 'message-response' },
      { kind: 'system', expectedClass: 'message-system' },
      { kind: 'error', expectedClass: 'message-error' }
    ]

    testCases.forEach(({ kind, expectedClass }) => {
      const message: ConversationMessage = {
        parts: [mockMessagePart],
        kind,
        timestamp: '2025-01-15T10:30:00.000Z'
      }

      const wrapper = mount(ChatMessage, {
        props: {
          messages: [message]
        }
      })

      expect(wrapper.find('.chat-message').classes()).toContain(expectedClass)
    })
  })

  it('applies correct CSS classes for different part kinds', () => {
    const testCases = [
      { part_kind: 'system-prompt', expectedClass: 'part-system' },
      { part_kind: 'user-prompt', expectedClass: 'part-user' },
      { part_kind: 'text', expectedClass: 'part-text' },
      { part_kind: 'tool-call', expectedClass: 'part-tool-call' },
      { part_kind: 'tool-return', expectedClass: 'part-tool-return' }
    ]

    testCases.forEach(({ part_kind, expectedClass }) => {
      const part: MessagePart = {
        content: 'Test content',
        timestamp: '2025-01-15T10:30:00.000Z',
        part_kind
      }

      const message: ConversationMessage = {
        parts: [part],
        kind: 'response',
        timestamp: '2025-01-15T10:30:00.000Z'
      }

      const wrapper = mount(ChatMessage, {
        props: {
          messages: [message],
          showDebugInfo: true // force affichage pour éviter le filtrage
        }
      })

      expect(wrapper.find('.message-part').classes()).toContain(expectedClass)
    })
  })
})
