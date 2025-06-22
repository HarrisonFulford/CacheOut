import Header from "@/components/Header";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div className="min-h-screen bg-black text-white">
      <Header />
      <main className="pt-16"> {/* Add padding to offset the fixed header */}
        <Outlet />
      </main>
    </div>
  );
};

export default Layout; 