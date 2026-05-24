import './globals.css'

export const metadata = {
  title: 'Neil Anderson',
  description: 'Personal site of Neil Anderson',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
