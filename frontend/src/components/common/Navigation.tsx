import { Link, useLocation } from "react-router-dom";
import { MagnifyingGlassIcon, BellIcon, Cog6ToothIcon, ArrowLeftOnRectangleIcon, UserIcon } from "@heroicons/react/24/outline";
import { Button, Avatar, Input } from "../ui";
import { useAuthStore } from "../../context/authStore";
import clsx from "clsx";
import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";

export default function Navigation() {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const navLinks = [
    { to: "/", label: "Dashboard" },
    { to: "/library", label: "Library" },
    { to: "/upload", label: "Upload" },
    { to: "/recommendations", label: "Recommendations" },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="font-bold text-2xl text-primary-600">
              SIGRAA
            </Link>
            
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={clsx(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive(link.to)
                      ? "bg-primary-50 text-primary-700"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  )}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden lg:block w-64">
              <Input
                type="text"
                placeholder="Search articles..."
                icon={MagnifyingGlassIcon}
                className="h-9"
              />
            </div>

            <Button variant="ghost" size="sm">
              <BellIcon className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </Button>

            <Menu as="div" className="relative">
              <Menu.Button variant="ghost" size="sm" as={Button}>
                <Cog6ToothIcon className="h-5 w-5" />
              </Menu.Button>
              
              <Transition
                as={Fragment}
                enter="transition ease-out duration-100"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
              >
                <Menu.Items className="absolute right-0 mt-2 w-48 origin-top-right bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <div className="py-1">
                    <Menu.Item>
                      {({ active }) => (
                        <div className={clsx(
                          'block w-full text-left px-4 py-2 text-sm border-b border-gray-200',
                          active ? 'bg-gray-100' : ''
                        )}>
                          <p className="font-medium text-gray-900">{user?.username || user?.email}</p>
                          <p className="text-gray-500 text-xs">{user?.email}</p>
                        </div>
                      )}
                    </Menu.Item>
                    
                    <Menu.Item>
                      {({ active }) => (
                        <button
                          className={clsx(
                            'flex items-center gap-2 w-full text-left px-4 py-2 text-sm',
                            active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                          )}
                          onClick={logout}
                        >
                          <ArrowLeftOnRectangleIcon className="h-4 w-4" />
                          Cerrar sesión
                        </button>
                      )}
                    </Menu.Item>
                  </div>
                </Menu.Items>
              </Transition>
            </Menu>

            {user && (
              <div className="flex items-center gap-2 pl-2 border-l border-gray-200">
                <Avatar
                  name={user.username || user.email}
                  size="sm"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
