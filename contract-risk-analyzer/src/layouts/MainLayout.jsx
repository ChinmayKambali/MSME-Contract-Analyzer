import Navbar from "./Navbar";
import Footer from "./Footer";

export default function MainLayout({ children }) {
  return (
    <div className="app-shell min-h-screen flex flex-col">
      <Navbar />
      <main className="w-full max-w-6xl mx-auto flex-1 px-5 py-8 sm:px-8 lg:py-12">
        {children}
      </main>
      <Footer />
    </div>
  );
}