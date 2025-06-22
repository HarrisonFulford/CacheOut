
import Header from "@/components/Header";
import BuyComputePanel from "@/components/BuyComputePanel";
import SellComputePanel from "@/components/SellComputePanel";

const Index = () => {
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Main Panels Section - True Full Screen */}
      <div className="h-screen">
        <div className="grid md:grid-cols-2 gap-0 h-full">
          <BuyComputePanel />
          <SellComputePanel />
        </div>
      </div>
      
      {/* Header overlaid on top */}
      <Header />
    </div>
  );
};

export default Index;
