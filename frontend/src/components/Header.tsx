import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";

const Header = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('isLoggedIn') === 'true';
  });

  const handleLogin = () => {
    localStorage.setItem('isLoggedIn', 'true');
    setIsLoggedIn(true);
    window.location.reload();
  };

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    setIsLoggedIn(false);
    window.location.reload();
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
      <div className="container mx-auto px-6 py-2">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <img 
              src="/lovable-uploads/b9c2b5d2-aef9-4d62-870b-e6ba7e389373.png" 
              alt="Cache Out Logo" 
              className="h-12 w-12"
            />
            <span className="text-xl font-bold text-white" style={{ fontFamily: 'Proxima Nova, sans-serif', marginTop: '2px' }}>CacheOut</span>
          </Link>

          <div className="hidden md:flex items-center space-x-4">
            {isLoggedIn ? (
              <span 
                className="text-white font-medium cursor-pointer hover:text-gray-300 transition-colors" 
                onClick={handleLogout}
              >
                Quandale Quandale
              </span>
            ) : (
              <>
                <Button variant="ghost" className="text-white hover:bg-white/10" onClick={handleLogin}>
                  Log In
                </Button>
                <Button className="bg-gradient-to-r from-emerald-500 to-blue-600 hover:from-emerald-600 hover:to-blue-700 text-white">
                  Sign Up
                </Button>
              </>
            )}
          </div>

          <Button variant="ghost" size="icon" className="md:hidden text-white">
            <Menu className="h-6 w-6" />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;
