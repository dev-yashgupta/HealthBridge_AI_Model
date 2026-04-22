import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="font-body selection:bg-secondary-fixed selection:text-on-secondary-fixed min-h-screen">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-[#1a1b21] opacity-80 backdrop-blur-md flex justify-between items-center px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full overflow-hidden outline outline-2 outline-secondary-fixed/30 p-0.5">
            <img 
              alt="User profile portrait" 
              className="w-full h-full object-cover rounded-full" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBDWbBKmbZcXKC0e1KV9RPtusHFjp0hpH8I-MNYBcsKow-tnDL2hgoN-WE0khvinPjZ2XvXJSKCHUkKlToum_Ph65vn-D3bhdXLhP77h5oEHMjTtvz643WjzxVAVIHrpNxc8iYwLow0wLzPXIjyZ_C6DvcjxZikBb0QI02zLUiLmB89UYTOVcYTyBqa46D1rAC9q1yuIraqpcLGh4LlRMrickTXV_Zd9HKjdDJJIM8zkp3LtMj5kFmzz1cLm-1JHCC1baKps_ELIOQ"
            />
          </div>
          <span className="font-headline font-semibold tracking-tight text-lg text-[#dae2ff]">HealthBridge</span>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 rounded-full hover:bg-[#2b2d35] transition-colors active:scale-95 duration-200">
            <span className="material-symbols-outlined text-[#dae2ff]">notifications</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="pt-24 pb-28">
        <Outlet />
      </div>

      {/* BottomNavBar */}
      <nav className="fixed bottom-0 w-full z-50 rounded-t-xl bg-[#1a1b21] border-t border-[#c4c6d3]/15 shadow-[0_-4px_20px_0_rgba(0,0,0,0.05)] flex justify-around items-center px-2 pb-safe pt-2">
        
        <NavLink 
          to="/"
          className={({ isActive }) => 
            `flex flex-col items-center justify-center rounded-xl px-4 py-1.5 transition-transform duration-150 active:scale-90 ${isActive ? 'bg-[#002869] text-[#dae2ff]' : 'text-[#c4c6d3] hover:bg-[#2b2d35]'}`
          }
        >
          <span className="material-symbols-outlined mb-0.5">home</span>
          <span className="font-['Inter'] text-[11px] font-medium">Home</span>
        </NavLink>

        <NavLink 
          to="/checker"
          className={({ isActive }) => 
            `flex flex-col items-center justify-center rounded-xl px-4 py-1.5 transition-transform duration-150 active:scale-90 ${isActive ? 'bg-[#002869] text-[#dae2ff]' : 'text-[#c4c6d3] hover:bg-[#2b2d35]'}`
          }
        >
          <span className="material-symbols-outlined mb-0.5">medical_services</span>
          <span className="font-['Inter'] text-[11px] font-medium">Checker</span>
        </NavLink>

        <NavLink 
          to="/history"
          className={({ isActive }) => 
            `flex flex-col items-center justify-center rounded-xl px-4 py-1.5 transition-transform duration-150 active:scale-90 ${isActive ? 'bg-[#002869] text-[#dae2ff]' : 'text-[#c4c6d3] hover:bg-[#2b2d35]'}`
          }
        >
          <span className="material-symbols-outlined mb-0.5">history</span>
          <span className="font-['Inter'] text-[11px] font-medium">History</span>
        </NavLink>

        <NavLink 
          to="/profile"
          className={({ isActive }) => 
            `flex flex-col items-center justify-center rounded-xl px-4 py-1.5 transition-transform duration-150 active:scale-90 ${isActive ? 'bg-[#002869] text-[#dae2ff]' : 'text-[#c4c6d3] hover:bg-[#2b2d35]'}`
          }
        >
          <span className="material-symbols-outlined mb-0.5">person</span>
          <span className="font-['Inter'] text-[11px] font-medium">Profile</span>
        </NavLink>

      </nav>
    </div>
  )
}
