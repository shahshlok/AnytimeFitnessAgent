// src/components/AetherialNebulaUI.jsx

import React from 'react';
import { Mic, User, Bot } from 'lucide-react';

// FIX #1: Using `export const` for a named export, which matches the import in App.jsx.
export const AetherialNebulaUI = ({ status = 'idle', conversation = [] }) => {
  // Define state classes for easier management
  const size = status === 'listening' ? 320 : status === 'processing' ? 280 : 300;
  const scale = status === 'listening' ? 1.1 : status === 'processing' ? 0.9 : 1;

  return (
    // FIX #3: Removed the full-screen container to make the component modular.
    // It will now be centered by its parent (App.jsx).
    <div className="flex flex-col items-center justify-center gap-12">

      {/* Custom Animations */}
      <style>
        {`
          @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.04); }
          }
          @keyframes vibrate {
            0%, 100% { transform: translate(0, 0); }
            25% { transform: translate(-2px, 2px); }
            50% { transform: translate(2px, -2px); }
            75% { transform: translate(-2px, -2px); }
          }
          @keyframes flash {
            0%, 100% { opacity: 0; }
            50% { opacity: 0.8; }
          }
          @keyframes energyStreak {
            0% { transform: translateX(100%) scale(0.5); opacity: 0; }
            50% { opacity: 0.8; }
            100% { transform: translateX(-100%) scale(0.5); opacity: 0; }
          }
          .energy-streak {
            position: absolute;
            width: 2px;
            height: 40px;
            background: linear-gradient(to right, transparent, theme('colors.lime.400'), transparent);
            animation: energyStreak 1.5s infinite;
          }
        `}
      </style>

      {/* Main Energy Core Container */}
      <div
        className="relative flex items-center justify-center transition-all duration-700 ease-in-out"
        style={{ width: size, height: size }}
      >
        <svg
          className="absolute w-full h-full"
          viewBox="0 0 400 400"
          style={{
            transform: `scale(${scale})`,
            transition: 'transform 0.7s ease-in-out',
            animation: status === 'idle' ? 'heartbeat 2s infinite ease-in-out' : 
                      status === 'processing' ? 'vibrate 0.2s infinite' : 'none'
          }}
        >
          <defs>
            <filter id="gooey">
              <feGaussianBlur in="SourceGraphic" stdDeviation="15" result="blur" />
              <feColorMatrix
                in="blur"
                mode="matrix"
                values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -10"
                result="goo"
              />
              <feBlend in="SourceGraphic" in2="goo" />
            </filter>
            <linearGradient id="energyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ec4899" /> {/* fuchsia-500 */}
              <stop offset="100%" stopColor="#a3e635" /> {/* lime-400 */}
            </linearGradient>
          </defs>
          <g filter="url(#gooey)">
            <circle cx="150" cy="150" r="80" className="fill-fuchsia-500/50 transition-colors duration-500" />
            <circle cx="250" cy="150" r="80" className="fill-fuchsia-600/50 transition-colors duration-500" />
            <circle cx="200" cy="250" r="70" className="fill-fuchsia-700/50 transition-colors duration-500" />
            
            {/* Energy Flash Effect */}
            {status === 'processing' && (
              <circle cx="200" cy="200" r="100" className="fill-lime-400/30" style={{ animation: 'flash 0.5s infinite' }} />
            )}

            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0 200 200"
              to="360 200 200"
              dur={status === 'processing' ? "5s" : "20s"}
              repeatCount="indefinite"
            />
          </g>
        </svg>

        {/* Energy Streaks for Listening State */}
        {status === 'listening' && (
          <>
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="energy-streak"
                style={{
                  transform: `rotate(${i * 45}deg)`,
                  animationDelay: `${i * 0.2}s`
                }}
              />
            ))}
          </>
        )}

        {/* Speaking Rings */}
        {status === 'speaking' && (
          <>
            <div className="absolute w-full h-full rounded-full border-2 border-lime-400/50 animate-ping" style={{ animationDuration: '1.5s' }}></div>
            <div className="absolute w-full h-full rounded-full border-2 border-lime-400/30 animate-ping" style={{ animationDuration: '1.5s', animationDelay: '0.5s' }}></div>
            <div className="absolute w-full h-full rounded-full border-2 border-lime-400/20 animate-ping" style={{ animationDuration: '1.5s', animationDelay: '1s' }}></div>
          </>
        )}

        {/* Mic Button */}
        {status === 'idle' && (
          <button
            className="absolute z-10 p-6 rounded-full bg-fuchsia-600/80 backdrop-blur-sm 
                     hover:bg-fuchsia-500 transition-all duration-300 transform hover:scale-110 
                     shadow-lg shadow-fuchsia-500/20"
          >
            <Mic className="w-12 h-12 text-slate-200" />
          </button>
        )}
      </div>

      {/* Conversation Echoes */}
      <div className="space-y-4 w-full max-w-2xl min-h-[150px]">
        {conversation.map((message, index) => (
          <div
            key={index}
            className="flex items-start space-x-3 p-4 rounded-lg bg-zinc-900/70 backdrop-blur-sm
                     border border-zinc-800/50 hover:border-fuchsia-500/30 transition-all duration-300
                     shadow-lg hover:shadow-fuchsia-500/10"
            style={{ opacity: 1 - index * 0.15, animationDelay: `${index * 100}ms` }}
          >
            {message.role === 'user' ? (
              <User className="w-6 h-6 text-fuchsia-500 mt-1 flex-shrink-0" />
            ) : (
              <Bot className="w-6 h-6 text-lime-400 mt-1 flex-shrink-0" />
            )}
            <p className="text-slate-200 font-sans text-lg">{message.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};