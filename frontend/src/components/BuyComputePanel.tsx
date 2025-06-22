
import { Button } from "@/components/ui/button";
import { ShoppingCart, Zap, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";

const BuyComputePanel = () => {
  const navigate = useNavigate();

  return (
    <div className="relative h-full group overflow-hidden">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center transition-all duration-[5000ms] group-hover:scale-105"
        style={{
          backgroundImage: "url('https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80')"
        }}
      />
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/80 via-purple-900/70 to-blue-900/80 group-hover:from-indigo-900/70 group-hover:via-purple-900/60 group-hover:to-blue-900/70 transition-all duration-[5000ms]" />
      
      {/* Full Screen Glassmorphism Overlay with split effect */}
      <div className="absolute inset-0 bg-white/5 backdrop-blur-xl border-r border-white/10 group-hover:bg-white/8 group-hover:backdrop-blur-sm transition-all duration-[3000ms] group-hover:w-[65%] group-hover:right-0">
        {/* Content Container */}
        <div className="h-full flex flex-col justify-center items-center text-center p-8">
          <div className="mb-6 p-4 bg-gradient-to-br from-indigo-500/20 to-purple-600/20 rounded-full backdrop-blur-sm group-hover:scale-105 transition-transform duration-[2000ms]">
            <ShoppingCart className="h-12 w-12 text-indigo-300" />
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent group-hover:scale-102 transition-transform duration-[2000ms]">
            Buy Compute
          </h2>
          
          <p className="text-lg text-gray-300 mb-8 max-w-md leading-relaxed group-hover:text-gray-200 transition-colors duration-[2000ms]">
            Access powerful GPU clusters and AI infrastructure on-demand. Scale your workloads instantly with enterprise-grade computing power.
          </p>
          
          <div className="flex items-center space-x-6 mb-8 text-sm text-gray-400 group-hover:text-gray-300 transition-colors duration-[2000ms]">
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-indigo-400" />
              <span>Instant Access</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-purple-400" />
              <span>24/7 Availability</span>
            </div>
          </div>
          
          <Button 
            size="lg" 
            onClick={() => navigate('/buyer-dashboard')}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-[2000ms] hover:scale-105 hover:shadow-2xl hover:shadow-indigo-500/25 group-hover:shadow-2xl group-hover:shadow-indigo-500/40"
          >
            Start Computing
          </Button>
        </div>
      </div>
    </div>
  );
};

export default BuyComputePanel;
