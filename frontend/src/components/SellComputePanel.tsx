
import { Button } from "@/components/ui/button";
import { DollarSign, TrendingUp, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

const SellComputePanel = () => {
  const navigate = useNavigate();

  return (
    <div className="relative h-full group overflow-hidden">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center transition-all duration-[2000ms] group-hover:scale-105"
        style={{
          backgroundImage: "url('https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80')"
        }}
      />
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/80 via-blue-900/70 to-cyan-900/80 group-hover:from-emerald-900/70 group-hover:via-blue-900/60 group-hover:to-cyan-900/70 transition-all duration-[2000ms]" />
      
      {/* Full Screen Glassmorphism Overlay with split effect */}
      <div className="absolute inset-0 bg-white/5 backdrop-blur-xl border-l border-white/10 group-hover:bg-white/8 group-hover:backdrop-blur-sm transition-all duration-1000 group-hover:w-[65%] group-hover:ml-[35%]">
        {/* Content Container */}
        <div className="h-full flex flex-col justify-center items-center text-center p-8">
          <div className="mb-6 p-4 bg-gradient-to-br from-emerald-500/20 to-blue-600/20 rounded-full backdrop-blur-sm group-hover:scale-105 transition-transform duration-500">
            <DollarSign className="h-12 w-12 text-emerald-300" />
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 bg-gradient-to-r from-emerald-300 to-blue-300 bg-clip-text text-transparent group-hover:scale-102 transition-transform duration-500">
            Sell Compute
          </h2>
          
          <p className="text-lg text-gray-300 mb-8 max-w-md leading-relaxed group-hover:text-gray-200 transition-colors duration-500">
            Monetize your idle hardware and earn passive income. Connect your GPUs and servers to our global compute marketplace.
          </p>
          
          <div className="flex items-center space-x-6 mb-8 text-sm text-gray-400 group-hover:text-gray-300 transition-colors duration-500">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-emerald-400" />
              <span>Passive Income</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-blue-400" />
              <span>Secure Platform</span>
            </div>
          </div>
          
          <Button 
            size="lg" 
            onClick={() => navigate('/seller-dashboard')}
            className="bg-gradient-to-r from-emerald-500 to-blue-600 hover:from-emerald-600 hover:to-blue-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-emerald-500/25 group-hover:shadow-2xl group-hover:shadow-emerald-500/40"
          >
            Start Earning
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SellComputePanel;
