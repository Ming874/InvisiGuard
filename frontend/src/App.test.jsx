import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders the main title', () => {
    render(<App />)
    expect(screen.getByText(/InvisiGuard/i)).toBeInTheDocument()
  })

  it('renders the Embed tab by default', () => {
    render(<App />)
    expect(screen.getByText(/1. Upload Image/i)).toBeInTheDocument()
  })
})
