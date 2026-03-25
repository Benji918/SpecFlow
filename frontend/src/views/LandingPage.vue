<template>
  <div class="min-h-screen bg-black text-white selection:bg-primary selection:text-black font-sans">
    <!-- Navbar -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-xl border-b border-white/5">
      <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center transform rotate-12 group-hover:rotate-0 transition-transform">
            <Zap :size="20" class="text-black fill-current" />
          </div>
          <span class="text-2xl font-black tracking-tighter">
            Spec<span class="text-primary">Flow</span>
          </span>
        </div>
        
        <div class="hidden md:flex items-center space-x-10 text-sm font-medium text-gray-400">
          <a href="#home" class="hover:text-primary transition-colors">Home</a>
          <a href="#features" class="hover:text-primary transition-colors">Features</a>
          <!-- <a href="#pricing" class="hover:text-primary transition-colors">Pricing</a> -->
          <a href="#contact" class="hover:text-primary transition-colors">Contact</a>
        </div>

        <div class="flex items-center space-x-4">
          <RouterLink to="/login" class="text-sm font-bold text-gray-400 hover:text-white transition-colors">Log in</RouterLink>
          <RouterLink to="/signup" class="px-5 py-2.5 bg-primary hover:bg-primary-dark text-black rounded-full text-sm font-black transition-all hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(191,245,73,0.3)]">
            Get Started
          </RouterLink>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="relative pt-32 pb-20 overflow-hidden">
      <!-- Background Glows -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-[radial-gradient(circle,rgba(191,245,73,0.1)_0%,transparent_70%)] -z-10 rounded-full"></div>
      
      <div class="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
        <div class="space-y-8 relative z-10">
          <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-primary text-xs font-bold uppercase tracking-widest">
            <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span>Next-Gen API Testing</span>
          </div>
          <h1 class="text-6xl lg:text-8xl font-black leading-[0.9] tracking-tighter">
            Test Smarter. <br/>
            <span class="relative inline-block mt-2">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-primary to-primary-dark">
                Flow Faster.
              </span>
              <!-- Hand-drawn Underline -->
              <svg class="absolute -bottom-4 left-0 w-full h-4 text-primary opacity-80" viewBox="0 0 300 20" fill="none" preserveAspectRatio="none">
                <path d="M5 15C50 5 150 5 295 15" stroke="currentColor" stroke-width="4" stroke-linecap="round" class="underline-path" />
              </svg>
            </span>
          </h1>
          <p class="text-xl text-gray-400 max-w-xl leading-relaxed">
            Turn OpenAPI specs into interactive user journeys. Automate data chaining and gain total visibility into your API flows.
          </p>
          <div class="flex flex-col sm:flex-row items-center gap-4">
            <RouterLink to="/signup" class="w-full sm:w-auto px-8 py-4 bg-primary text-black rounded-2xl text-lg font-black hover:bg-white transition-all shadow-xl hover:shadow-primary/20 flex items-center justify-center group">
              Start Free Journey
              <ArrowRight class="ml-2 group-hover:translate-x-1 transition-transform" />
            </RouterLink>
            <a href="#demo" class="w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 text-white rounded-2xl text-lg font-bold hover:bg-white/10 transition-all text-center">
              Watch Demo
            </a>
          </div>
        </div>

        <!-- Interactive Product Preview -->
        <div class="relative group">
          <div class="absolute inset-0 bg-[radial-gradient(circle,rgba(191,245,73,0.15)_0%,transparent_70%)] -z-10 rounded-3xl group-hover:bg-primary/20 transition-all duration-700"></div>
          <div class="relative bg-gray-900/40 border border-white/10 rounded-[40px] p-6 shadow-2xl backdrop-blur-xl ring-1 ring-white/10 overflow-hidden min-h-[500px]"
               @mousemove="handleDragMove" @mouseup="handleDragEnd" @mouseleave="handleDragEnd"
               @touchmove="handleDragMove" @touchend="handleDragEnd" @touchcancel="handleDragEnd">
            <!-- Mock UI Overlay -->
            <div class="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
              <div class="flex items-center space-x-3">
                <div class="flex space-x-1.5">
                   <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
                   <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                   <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <div class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-mono text-gray-400">
                  specflow
                </div>
              </div>
              <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-1 text-[10px] text-primary/80 font-bold uppercase tracking-widest">
                  <Zap :size="10" />
                  <span>Real-time Sync</span>
                </div>
              </div>
            </div>

            <!-- Canvas Area (Draggable Nodes) -->
            <div class="relative h-[350px] w-full">
              <!-- Edge Lines -->
              <svg class="absolute inset-0 w-full h-full pointer-events-none">
                <template v-for="(node, index) in nodes" :key="'edge-' + index">
                  <line 
                    v-if="index < nodes.length - 1"
                    :x1="node.x + 64" :y1="node.y + 40" 
                    :x2="nodes[index+1].x + 64" :y2="nodes[index+1].y + 40" 
                    stroke="rgba(191,245,73,0.3)" 
                    stroke-width="2" 
                    stroke-dasharray="4"
                    class="animate-pulse"
                  />
                </template>
              </svg>

              <!-- Draggable Nodes -->
              <div 
                v-for="node in nodes" 
                :key="node.id"
                class="absolute w-32 cursor-move select-none touch-none"
                :style="{ left: node.x + 'px', top: node.y + 'px' }"
                @mousedown="handleDragStart($event, node.id)"
                @touchstart="handleDragStart($event, node.id)"
              >
                <div :class="[
                  'p-3 border rounded-xl backdrop-blur-md transition-colors group/node relative',
                  node.type === 'active' ? 'bg-primary/5 border-primary/20 shadow-[0_0_30px_rgba(191,245,73,0.1)]' : 'bg-white/5 border-white/10 shadow-xl'
                ]">
                  <div class="text-[8px] uppercase mb-1 font-bold" :class="node.type === 'active' ? 'text-primary' : 'text-gray-500'">Step {{ node.step }}</div>
                  <div class="text-[10px] font-black truncate" :class="node.type === 'active' ? 'text-white' : 'group-hover/node:text-primary transition-colors'">{{ node.label }}</div>
                  
                  <Zap v-if="node.type === 'active'" :size="12" class="absolute -right-2 -top-2 text-primary animate-float" />
                  
                  <!-- Small visual decoration for the node -->
                  <div v-if="node.id === 'node1'" class="mt-2 flex space-x-1">
                    <div class="w-full h-1 bg-primary/20 rounded-full overflow-hidden">
                      <div class="h-full bg-primary animate-[loading_2s_infinite]"></div>
                    </div>
                  </div>
                  <div v-if="node.context" class="mt-2 text-[8px] font-mono text-gray-500 italic">{{ node.context }}</div>
                </div>
              </div>

              <!-- Floating Context Bubble -->
              <div class="absolute right-0 top-0 p-4 transform translate-x-4 -translate-y-4">
                <div class="bg-black/60 border border-white/10 p-3 rounded-2xl backdrop-blur-xl shadow-2xl animate-float">
                  <div class="flex items-center space-x-2 mb-2">
                    <div class="w-2 h-2 rounded-full bg-blue-400"></div>
                    <span class="text-[9px] font-bold text-gray-400">Extracted Session</span>
                  </div>
                  <div class="space-y-1">
                    <div class="flex justify-between text-[8px] font-mono">
                      <span class="text-gray-600">userID:</span>
                      <span class="text-blue-400">"usr_9x21"</span>
                    </div>
                    <div class="flex justify-between text-[8px] font-mono">
                      <span class="text-gray-600">token:</span>
                      <span class="text-primary italic">"***"</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Bar -->
            <div class="mt-8 pt-6 border-t border-white/5 flex items-center justify-between">
              <div class="flex -space-x-2">
                <div v-for="i in 3" :key="i" class="w-8 h-8 rounded-full border-2 border-gray-900 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center shadow-inner group/avatar hover:border-primary/30 transition-all">
                  <Zap :size="10" :class="['text-primary/60 fill-current', i === 2 ? 'opacity-100' : i === 1 ? 'opacity-70' : 'opacity-50']" />
                </div>
              </div>
              <div class="flex flex-col items-end">
                <span class="text-[10px] font-black uppercase text-gray-500 mb-1">Try moving the nodes</span>
                <div class="px-4 py-2 bg-primary rounded-lg text-[10px] font-black text-black shadow-[0_0_20px_rgba(191,245,73,0.4)]">
                   ACTIVE SESSION
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Journey Discovery & Chaining Pipeline Illustration -->
    <section class="py-24 relative overflow-hidden bg-black border-y border-white/5">
      <!-- Background Ambient Glow -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(191,245,73,0.03)_0%,transparent_70%)] pointer-events-none"></div>
      
      <div class="max-w-7xl mx-auto px-6 relative z-10">
        <!-- Header -->
        <div class="text-center mb-24 space-y-4">
          <div class="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-widest mb-4">
            <Sparkles :size="12" class="fill-current" />
            <span>The SpecFlow Method</span>
          </div>
          <h2 class="text-5xl lg:text-7xl font-black tracking-tight leading-none uppercase">
            From Spec to <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary via-white to-primary">Smart Execution</span>
          </h2>
        </div>

        <!-- The 3 Phases -->
        <div class="grid lg:grid-cols-3 gap-10 relative">
          <!-- Connection Path (Visual only) -->
          <div class="hidden lg:block absolute top-[120px] left-[15%] right-[15%] h-[2px] bg-gradient-to-r from-transparent via-primary/20 to-transparent -z-10">
            <div class="absolute inset-0 bg-primary/40 blur-sm animate-pulse"></div>
          </div>
          
          <!-- Phase 1: AI/Manual Inference -->
          <div class="group relative bg-[#0A0A0A] border border-white/10 p-8 rounded-[40px] hover:border-primary/40 transition-all duration-700 shadow-3xl hover:shadow-primary/5">
            <div class="absolute -top-10 -right-10 w-40 h-40 bg-primary/5 blur-3xl rounded-full group-hover:bg-primary/10 transition-all"></div>
            
            <div class="relative z-10 flex flex-col h-full">
              <div class="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mb-8 shadow-[0_0_30px_rgba(191,245,73,0.3)] group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
                <Bot :size="32" class="text-black" />
              </div>
              
              <div class="space-y-3 mb-8">
                <h3 class="text-xl font-black text-white">1. Intelligent Discovery</h3>
                <p class="text-gray-400 leading-relaxed text-[13px]">
                  SpecFlow's <span class="text-white font-bold italic">Inference Engine</span> scans your endpoints to map out every dependency and auto-suggest logical user journeys.
                </p>
              </div>

              <!-- Terminal-style UI Component -->
              <div class="mt-auto relative bg-black/60 rounded-2xl border border-white/10 p-6 font-mono text-[11px] overflow-hidden group/terminal border-t-primary/20 min-h-[180px] flex flex-col">
                <div class="flex items-center space-x-2 mb-6 border-b border-white/5 pb-3">
                  <div class="w-2 h-2 rounded-full bg-red-500/50"></div>
                  <div class="w-2 h-2 rounded-full bg-yellow-500/50"></div>
                  <div class="w-2 h-2 rounded-full bg-green-500/50"></div>
                  <span class="text-[9px] text-gray-500 ml-2 tracking-widest uppercase font-bold">inference_engine.log</span>
                </div>
                <div class="space-y-2 text-gray-400 flex-1">
                  <div class="flex items-center space-x-2">
                    <span class="text-primary font-bold">></span>
                    <span class="animate-pulse">Analyzing endpoint relationships...</span>
                  </div>
                  <div class="pl-5 opacity-50 text-[10px]">✓ Identified 'auth_session' flow across 4 nodes</div>
                  <div class="pl-5 opacity-50 text-[10px]">✓ Extracting 'order_id' from POST /orders</div>
                  <div class="flex items-center space-x-2 py-2">
                    <span class="text-primary font-bold">></span>
                    <span class="text-white font-black">Success:</span>
                    <span class="text-primary bg-primary/10 px-1.5 py-0.5 rounded">"E-Commerce Flow" Generated</span>
                  </div>
                </div>
                <!-- Scanning Effect -->
                <div class="absolute top-0 left-0 w-full h-[1.5px] bg-primary/30 shadow-[0_0_20px_rgba(191,245,73,0.6)] animate-[scan_4s_linear_infinite]"></div>
              </div>
            </div>
          </div>

          <!-- Phase 2: Flowchart Manner UI -->
          <div class="group relative bg-[#0A0A0A] border border-white/10 p-8 rounded-[40px] hover:border-primary/40 transition-all duration-700 shadow-3xl lg:translate-y-12">
            <div class="relative z-10 flex flex-col h-full">
              <div class="w-16 h-16 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-center mb-8 mx-auto group-hover:border-primary/50 transition-colors">
                <Workflow :size="32" class="text-primary group-hover:animate-spin-slow" />
              </div>
              
              <div class="space-y-3 mb-8 text-center">
                <h3 class="text-xl font-black text-white">2. Flowchart Control</h3>
                <p class="text-gray-400 leading-relaxed text-[13px]">
                  Take full control of the execution order with a flowchart UI. Drag, drop, and link any request to build your ideal test scenario.
                </p>
              </div>

              <!-- Flowchart Visual -->
              <div class="mt-auto relative h-52 bg-[#050505] rounded-2xl border border-white/5 overflow-hidden flex flex-col justify-center items-center shadow-inner">
                <div class="absolute inset-0 bg-[radial-gradient(#ffffff05_1.5px,transparent_1.5px)] bg-[size:24px_24px]"></div>
                
                <div class="relative flex flex-col space-y-6 items-center">
                  <!-- Top Node -->
                  <div class="w-32 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center space-x-3 backdrop-blur-md group-hover:border-primary/20 transition-colors">
                    <div class="w-2 h-2 rounded-full bg-primary/40 animate-pulse"></div>
                    <span class="text-[10px] font-black text-gray-300 uppercase tracking-tighter">POST: Login</span>
                  </div>
                  
                  <!-- Connection Line -->
                  <div class="w-[2px] h-10 bg-gradient-to-b from-primary/50 to-primary/5 relative">
                    <div class="absolute top-0 -left-[1.5px] w-[5px] h-4 bg-gradient-to-t from-primary to-transparent blur-[1px] rounded-full animate-flow-down"></div>
                    <!-- Flow indicator label -->
                    <div class="absolute top-1/2 left-4 -translate-y-1/2 px-2 py-0.5 bg-black/80 border border-white/10 rounded text-[7px] font-mono text-primary/60 whitespace-nowrap">
                      on_success →
                    </div>
                  </div>

                  <!-- Bottom Node -->
                  <div class="w-32 h-12 bg-primary/10 border-2 border-primary/40 rounded-xl flex items-center justify-center space-x-3 shadow-[0_0_30px_rgba(191,245,73,0.15)] group-hover:scale-105 transition-transform duration-500">
                    <div class="w-2 h-2 rounded-full bg-primary animate-ping"></div>
                    <span class="text-[10px] font-black text-white uppercase tracking-tighter">GET: Profile</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Phase 3: Optimized Data Linking -->
          <div class="group relative bg-[#0A0A0A] border border-white/10 p-8 rounded-[40px] hover:border-primary/40 transition-all duration-700 shadow-3xl">
            <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-primary/5 blur-3xl rounded-full group-hover:bg-primary/10 transition-all"></div>
            
            <div class="relative z-10 flex flex-col h-full">
              <div class="w-16 h-16 bg-primary/10 border border-primary/20 rounded-2xl flex items-center justify-center mb-8">
                <Link :size="32" class="text-primary animate-pulse" />
              </div>
              
              <div class="space-y-3 mb-8">
                <h3 class="text-xl font-black text-white">3. Smart Data Chaining</h3>
                <p class="text-gray-400 leading-relaxed text-[13px]">
                  SpecFlow automatically links response fields to subsequent requests. Optimized data transmission without ever lifting a finger.
                </p>
              </div>

              <!-- High-Fidelity Chaining Visual -->
              <div class="mt-auto relative space-y-3 bg-[#050505] p-5 rounded-2xl border border-white/5 overflow-hidden border-b-primary/20">
                <!-- Source Code -->
                <div class="bg-white/5 rounded-xl p-3 border border-white/5 group/code cursor-default hover:bg-white/10 transition-colors">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[8px] text-gray-500 uppercase font-black tracking-widest">RES_STEP1</span>
                    <div class="flex space-x-1">
                      <div class="w-1 h-1 rounded-full bg-gray-700"></div>
                      <div class="w-1 h-1 rounded-full bg-gray-700"></div>
                    </div>
                  </div>
                  <div class="text-[10px] font-mono text-gray-400 truncate">
                    &lbrace; "token": <span class="text-primary font-bold animate-[pulse_2s_infinite]">"SF_9xK..."</span> &rbrace;
                  </div>
                </div>

                <!-- Animated Data Stream -->
                <div class="h-6 flex justify-center items-center relative gap-2">
                   <div class="w-px h-full bg-gradient-to-b from-primary/50 to-transparent relative">
                      <div class="absolute top-0 -left-[2px] w-[5px] h-[5px] bg-primary rounded-full blur-[1px] animate-[drop_1.5s_infinite]"></div>
                   </div>
                   <span class="text-[7px] text-primary/40 font-mono italic">linking_parameter...</span>
                </div>

                <!-- Target Code -->
                <div class="bg-primary/5 rounded-xl p-3 border border-primary/20 opacity-80 group/code cursor-default hover:opacity-100 transition-opacity">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[8px] text-primary uppercase font-black tracking-widest">REQ_STEP2</span>
                  </div>
                  <div class="text-[10px] font-mono text-gray-500">
                    HTTP GET <span class="text-white font-bold">&lbrace; auth_token &rbrace;</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Video Showcase Section -->
    <section class="py-32 relative overflow-hidden" id="demo">
      <!-- Background Effects -->
      <div class="absolute inset-0 bg-gradient-to-b from-black via-primary/5 to-black"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] bg-primary/10 blur-[200px] rounded-full"></div>
      
      <div class="max-w-7xl mx-auto px-6 relative z-10">
        <!-- Section Header -->
        <div class="text-center mb-16 space-y-4">
          <div class="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-widest mb-4">
            <Play :size="12" class="fill-current" />
            <span>See It In Action</span>
          </div>
          <h2 class="text-5xl lg:text-7xl font-black tracking-tight leading-none">
            Watch SpecFlow <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary via-white to-primary">Transform Your Workflow</span>
          </h2>
          <p class="text-gray-400 text-lg max-w-2xl mx-auto">
            See how SpecFlow turns complex API specs into visual, testable journeys in seconds.
          </p>
        </div>

        <!-- Video Container -->
        <div class="relative group max-w-6xl mx-auto">
          <!-- Glow Effect -->
          <div class="absolute -inset-4 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-[60px]"></div>
          
          <!-- Video Wrapper -->
          <div class="relative bg-gradient-to-br from-gray-900/90 to-black/90 rounded-[48px] p-4 border border-white/10 shadow-2xl backdrop-blur-xl overflow-hidden">
            <!-- Browser Chrome -->
            <div class="flex items-center justify-between mb-4 pb-4 border-b border-white/5">
              <div class="flex items-center space-x-3">
                <div class="flex space-x-2">
                  <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <div class="px-4 py-1.5 bg-white/5 rounded-full text-xs font-mono text-gray-400 flex items-center space-x-2">
                  <Lock :size="10" class="text-green-400" />
                  <span>specflow</span>
                </div>
              </div>
              <div class="flex items-center space-x-2 text-xs text-primary/80 font-bold uppercase tracking-widest">
                <Circle :size="8" class="fill-current animate-pulse" />
                <span>Live Demo</span>
              </div>
            </div>

            <!-- Video Player -->
            <div class="relative aspect-video bg-black rounded-3xl overflow-hidden shadow-2xl">
              <!-- Loading State -->
              <div v-if="videoLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-black z-20">
                <div class="relative">
                  <div class="w-20 h-20 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                  <Zap :size="32" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-primary fill-current animate-pulse" />
                </div>
                <p class="mt-6 text-sm font-bold text-gray-400 uppercase tracking-widest">Loading Demo...</p>
                <div class="mt-4 w-48 h-1 bg-white/5 rounded-full overflow-hidden">
                  <div class="h-full bg-primary animate-[loading_2s_ease-in-out_infinite]" :style="{width: videoProgress + '%'}"></div>
                </div>
              </div>

              <!-- Buffering Indicator -->
              <div v-if="videoBuffering && !videoLoading" class="absolute top-4 right-4 z-30 flex items-center space-x-2 px-3 py-2 bg-black/80 backdrop-blur-md rounded-full border border-white/10">
                <Loader2 :size="14" class="text-primary animate-spin" />
                <span class="text-xs font-bold text-gray-400">Buffering...</span>
              </div>

              <!-- Video Element -->
              <video
                ref="demoVideo"
                class="w-full h-full object-cover"
                @loadstart="handleVideoLoadStart"
                @loadeddata="handleVideoLoaded"
                @waiting="videoBuffering = true"
                @playing="videoBuffering = false"
                @canplay="videoBuffering = false"
                @ended="handleVideoEnded"
                @timeupdate="handleTimeUpdate"
                preload="metadata"
                playsinline
              >
                <source src="/Specflow recroding.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>

              <!-- Play Overlay (when paused) -->
              <div 
                v-if="!videoPlaying && !videoLoading" 
                class="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer group/play z-10"
                @click="togglePlay"
              >
                <div class="w-24 h-24 rounded-full bg-primary/90 flex items-center justify-center shadow-[0_0_60px_rgba(191,245,73,0.6)] group-hover/play:scale-110 group-hover/play:bg-primary transition-all">
                  <Play :size="40" class="text-black fill-current ml-1" />
                </div>
              </div>

              <!-- Custom Controls -->
              <div 
                v-if="!videoLoading"
                class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-6 opacity-0 group-hover:opacity-100 transition-opacity z-20"
              >
                <!-- Progress Bar -->
                <div class="mb-4">
                  <div 
                    class="h-1.5 bg-white/20 rounded-full overflow-hidden cursor-pointer group/progress"
                    @click="seekVideo"
                    ref="progressBar"
                  >
                    <div class="h-full bg-primary rounded-full transition-all group-hover/progress:h-2" :style="{width: videoProgress + '%'}"></div>
                  </div>
                </div>

                <!-- Control Buttons -->
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-4">
                    <button 
                      @click="togglePlay"
                      class="w-10 h-10 rounded-full bg-white/10 hover:bg-primary hover:text-black flex items-center justify-center transition-all group/btn"
                    >
                      <Play v-if="!videoPlaying" :size="18" class="fill-current ml-0.5" />
                      <Pause v-else :size="18" class="fill-current" />
                    </button>
                    
                    <button 
                      @click="toggleMute"
                      class="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all"
                    >
                      <Volume2 v-if="!videoMuted" :size="18" />
                      <VolumeX v-else :size="18" />
                    </button>

                    <div class="text-xs font-mono text-gray-400">
                      {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
                    </div>
                  </div>

                  <button 
                    @click="toggleFullscreen"
                    class="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all"
                  >
                    <Maximize :size="18" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Video Stats -->
            <div class="mt-6 flex items-center justify-center space-x-8 text-xs">
              <div class="flex items-center space-x-2 text-gray-500">
                <Eye :size="14" />
                <span class="font-bold">Real Product Demo</span>
              </div>
              <div class="flex items-center space-x-2 text-gray-500">
                <Clock :size="14" />
                <span class="font-bold">{{ formatTime(duration) }} Full Walkthrough</span>
              </div>
              <div class="flex items-center space-x-2 text-primary">
                <Sparkles :size="14" />
                <span class="font-bold">No Fluff, Pure Value</span>
              </div>
            </div>
          </div>
        </div>

        <!-- CTA Below Video -->
        <div class="mt-16 text-center">
          <p class="text-gray-400 mb-6">Ready to experience this yourself?</p>
          <RouterLink 
            to="/signup" 
            class="inline-flex items-center px-8 py-4 bg-primary text-black rounded-2xl text-lg font-black hover:bg-white transition-all shadow-xl hover:shadow-primary/20 group"
          >
            Start Your Free Journey
            <ArrowRight class="ml-2 group-hover:translate-x-1 transition-transform" />
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Comparison Section (Redesigned) -->
    <section class="py-32 relative overflow-hidden">
      <!-- Decorator Icons -->
      <div class="absolute top-0 left-0 p-20 text-white/5 -rotate-12 pointer-events-none">
        <XCircle :size="300" />
      </div>
      <div class="absolute bottom-0 right-0 p-20 text-primary/5 rotate-12 pointer-events-none">
        <Zap :size="300" />
      </div>

      <div class="max-w-7xl mx-auto px-6 relative z-10">
         <div class="text-center mb-24 space-y-4">
            <h2 class="text-5xl lg:text-7xl font-black tracking-tight leading-none uppercase">
              The <span class="text-primary underline decoration-primary/30 underline-offset-8 italic">10x Leap</span> <br/>
              in API Testing
            </h2>
            <p class="text-gray-500 text-lg max-w-2xl mx-auto">Stop wasting hours on manual setup. Let SpecFlow handle the context while you focus on the flow.</p>
         </div>

         <div class="grid lg:grid-cols-11 gap-4 items-center">
            <!-- Traditional -->
            <div class="lg:col-span-5 bg-stone-900/50 border border-white/5 rounded-[40px] p-10 backdrop-blur-sm grayscale opacity-60 hover:grayscale-0 hover:opacity-100 h-full transition-all duration-500 group">
               <div class="flex items-center justify-between mb-10">
                 <h3 class="text-2xl font-bold text-gray-400 group-hover:text-white transition-colors">Manual Chaos</h3>
                 <div class="p-3 bg-red-500/10 rounded-2xl">
                   <AlertCircle :size="32" class="text-red-500" />
                 </div>
               </div>
               <ul class="space-y-6">
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-500"></div>
                    <div>
                      <h4 class="font-bold text-gray-300">Infinite Copy-Paste</h4>
                      <p class="text-sm text-gray-500">Copying tokens, IDs, and payloads between requests manually.</p>
                    </div>
                  </li>
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-500"></div>
                    <div>
                      <h4 class="font-bold text-gray-300">Brittle Collections</h4>
                      <p class="text-sm text-gray-500">One field change in your spec breaks every manual test you've built.</p>
                    </div>
                  </li>
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-500"></div>
                    <div>
                      <h4 class="font-bold text-gray-300">Zero Visibility</h4>
                      <p class="text-sm text-gray-500">Testing endpoints in silos. No way to visualize the end-to-end user path.</p>
                    </div>
                  </li>
               </ul>
            </div>

            <!-- VS Badge -->
            <div class="lg:col-span-1 flex justify-center py-8 lg:py-0">
              <div class="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-black font-black text-xl shadow-[0_0_30px_rgba(191,245,73,0.5)] z-20">
                VS
              </div>
            </div>

            <!-- SpecFlow -->
            <div class="lg:col-span-5 bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-[40px] p-10 shadow-[0_0_80px_rgba(191,245,73,0.1)] h-full relative overflow-hidden group">
               <!-- Animated background mesh -->
               <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(191,245,73,0.1)_0%,transparent_70%)]"></div>
               
               <div class="flex items-center justify-between mb-10 relative z-10">
                 <h3 class="text-3xl font-black text-primary">SpecFlow Confidence</h3>
                 <div class="p-3 bg-primary/10 rounded-2xl group-hover:scale-110 transition-transform duration-500">
                   <Zap :size="32" class="text-primary fill-current" />
                 </div>
               </div>
               <ul class="space-y-6 relative z-10">
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_10px_rgba(191,245,73,1)]"></div>
                    <div>
                      <h4 class="font-black text-white">Context-Aware Automation</h4>
                      <p class="text-sm text-gray-400">SpecFlow understands your API. It chains data flows automatically.</p>
                    </div>
                  </li>
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_10px_rgba(191,245,73,1)]"></div>
                    <div>
                      <h4 class="font-black text-white">Always-In-Sync</h4>
                      <p class="text-sm text-gray-400">Your visual journeys update the moment your OpenAPI spec changes.</p>
                    </div>
                  </li>
                  <li class="flex items-start space-x-4">
                    <div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_10px_rgba(191,245,73,1)]"></div>
                    <div>
                      <h4 class="font-black text-white">Visual Storytelling</h4>
                      <p class="text-sm text-gray-400">Collaborate with visual graphs that explain exactly how your product works.</p>
                    </div>
                  </li>
               </ul>
               <div class="mt-10 pt-10 border-t border-white/5 flex items-center justify-between relative z-10">
                  <span class="text-primary font-black tracking-widest uppercase text-xs">90% Productivity Boost</span>
                  <div class="flex space-x-1">
                     <div v-for="i in 5" :key="i" class="w-1 h-3 bg-primary/30 rounded-full group-hover:bg-primary transition-all" :style="{animationDelay: i*0.1 + 's'}"></div>
                  </div>
               </div>
            </div>
         </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section id="features" class="py-32 bg-white/5 border-y border-white/5">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex flex-col md:flex-row items-end justify-between mb-20 gap-8">
           <div class="space-y-4">
              <h2 class="text-5xl font-black tracking-tighter">Everything you need to <br/> scale API confidence.</h2>
              <p class="text-gray-400 max-w-lg">We've built all the core features to transform your OpenAPI specs into professional-grade test suites.</p>
           </div>
           <RouterLink to="/signup" class="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all font-bold group">
             Explore all features <ArrowRight :size="18" class="inline ml-2 group-hover:translate-x-1 transition-transform" />
           </RouterLink>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="card-feature group">
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <Bot :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">AI Journey Inference</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Our AI automatically analyzes your endpoints to suggest logical user workflows like "Checkout" or "Profile Setup".
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="card-feature group">
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <Workflow :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">Visual Workflow Builder</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Drag-and-drop nodes to reorganize your API sequence. Seeing is believing. No code required.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="card-feature group">
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <Database :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">Mock Data Generation</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Context-aware data generators create realistic emails, UUIDs, and numbers that perfectly match your schema.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="card-feature group">
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <Layers :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">Smart Session Management</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Automatically extract tokens from one step and inject them into the next. Zero manual intervention.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="card-feature group">
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <ShieldAlert :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">Error Injection</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Simulate network failures, 500 errors, or slow responses with a single click to test your frontend resilience.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="card-feature group relative overflow-hidden">
            <!-- Coming Soon Badge -->
            <div class="absolute top-4 right-4 z-10">
              <div class="px-3 py-1.5 bg-primary/10 border border-primary/30 rounded-full flex items-center space-x-2 shadow-[0_0_20px_rgba(191,245,73,0.15)]">
                <Clock :size="12" class="text-primary animate-pulse" />
                <span class="text-[10px] font-black uppercase tracking-widest text-primary">Coming Soon</span>
              </div>
            </div>
            <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-all">
               <Share2 :size="24" />
            </div>
            <h4 class="text-xl font-bold mb-3 tracking-tight">Export & Collaborate</h4>
            <p class="text-gray-400 text-sm leading-relaxed">
              Export your journeys to Postman or share interactive links with your team. Seamless handoff.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Section -->
    <!-- <section id="pricing" class="py-32 bg-white/5 border-y border-white/5 overflow-hidden relative"> -->
      <!-- <div class="absolute bottom-0 right-0 w-[800px] h-[800px] bg-primary/5 blur-[120px] rounded-full translate-x-1/2 translate-y-1/2"></div>
      <div class="max-w-7xl mx-auto px-6 text-center">
        <div class="mb-20 space-y-4">
          <h2 class="text-5xl font-black tracking-tight">Pricing that grows with you.</h2>
          <p class="text-gray-400">Simple, transparent plans for every team size.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto"> -->
          <!-- Free Plan -->
          <!-- <div class="bg-black border border-white/10 rounded-[32px] p-10 text-left flex flex-col hover:border-white/20 transition-colors">
             <div class="mb-8">
               <h4 class="text-xl font-bold mb-2">Free</h4>
               <div class="flex items-baseline mb-4">
                 <span class="text-4xl font-black">$0</span>
                 <span class="text-gray-500 ml-2">/forever</span>
               </div>
               <p class="text-gray-400 text-sm">Perfect for individuals and small side projects.</p>
             </div>
             <ul class="space-y-4 mb-10 flex-1">
                <li class="flex items-center space-x-3 text-sm text-gray-400">
                  <Check :size="16" class="text-primary" />
                  <span>3 Saved Journeys</span>
                </li>
                <li class="flex items-center space-x-3 text-sm text-gray-400">
                  <Check :size="16" class="text-primary" />
                  <span>Manual Journey Builder</span>
                </li>
                <li class="flex items-center space-x-3 text-sm text-gray-400">
                  <Check :size="16" class="text-primary" />
                  <span>Basic Mock Data</span>
                </li>
             </ul>
             <RouterLink to="/signup" class="w-full py-4 text-center rounded-2xl border border-white/10 hover:bg-white/5 transition-all font-bold">
               Get Started
             </RouterLink>
          </div> -->

          <!-- Pro Plan -->
          <!-- <div class="bg-black border-2 border-primary rounded-[32px] p-10 text-left flex flex-col relative overflow-hidden shadow-[0_0_50px_rgba(191,245,73,0.1)]">
             <div class="absolute top-0 right-0 px-4 py-1 bg-primary text-black text-[10px] font-black uppercase tracking-widest rounded-bl-xl">Popular</div>
             <div class="mb-8">
               <h4 class="text-xl font-bold mb-2 text-primary">Pro</h4>
               <div class="flex items-baseline mb-4">
                 <span class="text-4xl font-black">$9</span>
                 <span class="text-gray-500 ml-2">/month</span>
               </div>
               <p class="text-gray-400 text-sm">Everything you need for serious development.</p>
             </div>
             <ul class="space-y-4 mb-10 flex-1">
                <li class="flex items-center space-x-3 text-sm">
                  <Check :size="16" class="text-primary" />
                  <span><strong>Unlimited</strong> Journeys</span>
                </li>
                <li class="flex items-center space-x-3 text-sm">
                  <Check :size="16" class="text-primary" />
                  <span><strong>AI Powered</strong> Journey Inference</span>
                </li>
                <li class="flex items-center space-x-3 text-sm">
                  <Check :size="16" class="text-primary" />
                  <span>Team Collaboration & Sharing (Coming Soon)</span>
                </li>
             </ul>
             <RouterLink to="/signup" class="w-full py-4 text-center rounded-2xl bg-primary text-black font-black hover:bg-white transition-all shadow-[0_10px_30px_rgba(191,245,73,0.3)]">
               Upgrade to Pro
             </RouterLink>
          </div>
        </div>
      </div> -->
    <!-- </section> -->

    <!-- Contact Form Section -->
    <section id="contact" class="py-32 relative">
      <div class="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-20 items-center">
        <div class="space-y-8">
          <h2 class="text-5xl font-black tracking-tighter">Ready to sync? <br/> <span class="text-primary">Get in touch.</span></h2>
          <p class="text-gray-400 text-lg leading-relaxed">
            Have questions about integrating SpecFlow into your CI/CD pipeline or custom enterprise needs? We're here to help.
          </p>
          <!-- <div class="space-y-4"> -->
             <div class="flex items-center space-x-4">
                <!-- <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  <Mail :size="20" />
                </div> -->
                <!-- <a href="mailto:benjamin_kodi@outlook.com" class="text-gray-300 font-bold hover:text-primary transition-colors">benjamin_kodi@outlook.com</a> -->
             </div>
             <!-- <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  <MapPin :size="20" />
                </div>
                <span class="text-gray-300 font-bold">San Francisco, CA</span>
             </div> -->
          <!-- </div> -->
        </div>

        <!-- Contact Form (Commented out) -->
        <!-- 
        <div class="bg-white/5 border border-white/10 rounded-[40px] p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
           <div class="absolute -top-10 -right-10 w-32 h-32 bg-primary/20 blur-3xl rounded-full"></div>
           
           <form @submit.prevent class="space-y-6 relative z-10">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-500 tracking-widest pl-1">Name</label>
                  <input type="text" placeholder="John Doe" class="w-full bg-black/50 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all" required="true"/>
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-500 tracking-widest pl-1">Email</label>
                  <input type="email" placeholder="john@company.com" class="w-full bg-black/50 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all" required="true"/>
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-black uppercase text-gray-500 tracking-widest pl-1">Message</label>
                <textarea rows="4" placeholder="How can we help your team?" class="w-full bg-black/50 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all resize-none" required="true"></textarea>
              </div>
              <button class="w-full py-5 bg-primary text-black font-black rounded-2xl hover:bg-white transition-all shadow-[0_10px_30px_rgba(191,245,73,0.3)]">
                Send Message
              </button>
           </form>
        </div>
        -->

        <!-- Stunning Direct Email Card -->
        <div class="bg-gradient-to-br from-primary/20 via-primary/5 to-transparent border border-primary/20 rounded-[48px] p-12 shadow-[0_0_100px_rgba(191,245,73,0.1)] relative overflow-hidden group">
          <!-- Animated Background mesh -->
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(191,245,73,0.15)_0%,transparent_70%)] opacity-50 group-hover:opacity-100 transition-opacity duration-700"></div>
          
          <div class="relative z-10 flex flex-col items-center text-center space-y-10">
            <!-- Icon with Glow -->
            <div class="relative">
              <div class="absolute inset-0 bg-primary blur-3xl opacity-20 scale-150 animate-pulse"></div>
              <div class="relative w-24 h-24 rounded-[32px] bg-primary/20 flex items-center justify-center text-primary group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-[0_0_40px_rgba(191,245,73,0.2)] border border-primary/30">
                <Mail :size="48" class="animate-float" />
              </div>
            </div>

            <div class="space-y-4">
              <h3 class="text-4xl font-black text-white tracking-tight">Direct Access</h3>
              <p class="text-gray-400 max-w-sm mx-auto text-lg leading-relaxed">
                Skip the bureaucracy. Get a direct line to the founder for priority support, partnership inquiries, or custom enterprise solutions.
              </p>
            </div>

            <!-- Mailto Link Button -->
            <a 
              href="mailto:benjamin_kodi@outlook.com" 
              class="group/btn relative inline-flex items-center justify-center px-10 py-6 bg-primary text-black font-black rounded-3xl hover:bg-white transition-all duration-300 shadow-[0_20px_50px_rgba(191,245,73,0.4)] hover:shadow-primary/60 hover:-translate-y-1 active:scale-95"
            >
              <div class="absolute inset-0 bg-white opacity-0 group-hover/btn:opacity-20 transition-opacity rounded-3xl"></div>
              <span class="text-xl">benjamin_kodi@outlook.com</span>
              <ArrowRight class="ml-4 w-6 h-6 group-hover/btn:translate-x-2 transition-transform duration-300" />
            </a>

            <!-- Subtle Micro-interaction -->
            <div class="pt-4 flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">
               <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
               <span>Available for you</span>
            </div>
          </div>

          <!-- Decorative elements -->
          <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-primary/10 blur-[80px] rounded-full"></div>
          <div class="absolute top-1/2 right-0 w-20 h-80 bg-primary/5 blur-[60px] rounded-full rotate-45 opacity-50"></div>
        </div>
      </div>
    </section>

    <!-- Footer (Cleaned) -->
    <footer class="py-12 border-t border-white/5 bg-black">
       <div class="max-w-7xl mx-auto px-6">
          <div class="flex flex-col md:flex-row items-center justify-between gap-10">
             <div class="flex items-center space-x-2">
                <Zap :size="24" class="text-primary fill-current" />
                <span class="text-2xl font-black tracking-tighter">SpecFlow</span>
             </div>
             
             <div class="flex items-center space-x-10 text-xs font-bold uppercase tracking-widest text-gray-500">
               <a href="#home" class="hover:text-primary transition-colors">Home</a>
               <a href="#features" class="hover:text-primary transition-colors">Features</a>
               <!-- <a href="#pricing" class="hover:text-primary transition-colors">Pricing</a> -->
               <a href="#contact" class="hover:text-primary transition-colors">Contact</a>
             </div>

             <div class="flex items-center space-x-4">
                <a href="https://x.com/code_benji" class="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-primary hover:text-black transition-all group" target="_blank">
                   <svg viewBox="0 0 24 24" class="w-[18px] h-[18px] group-hover:fill-current fill-white transition-colors" aria-hidden="true">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path>
                   </svg>
                </a>
                <a href="https://github.com/Benji918" class="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-primary hover:text-black transition-all group" target="_blank">
                   <Github :size="18" class="group-hover:fill-current" />
                </a>
                <a href="https://www.linkedin.com/in/ugobenjamin/" class="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-primary hover:text-black transition-all group" target="_blank">
                   <Linkedin :size="18" class="group-hover:fill-current" />
                </a>
             </div>
          </div>

          <div class="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
             <p class="text-[10px] text-gray-600 font-bold uppercase tracking-widest">
               &copy; 2026 SpecFlow. All rights reserved.
             </p>
             <!-- <div class="flex items-center space-x-6 text-[10px] text-gray-600 font-bold uppercase tracking-widest">
                <a href="#" class="hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" class="hover:text-white transition-colors">Terms of Service</a>
             </div> -->
          </div>
       </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Zap,
  ArrowRight,
  Globe,
  CheckCircle,
  XCircle,
  AlertCircle,
  Check,
  Bot,
  Workflow,
  Database,
  Layers,
  ShieldAlert,
  Share2,
  Quote,
  Clock,
  Github,
  Linkedin,
  Mail,
  MapPin,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Lock,
  Circle,
  Loader2,
  Eye,
  Sparkles,
  Link
} from 'lucide-vue-next'

// Interactive Node State
const nodes = ref([
  { id: 'node1', x: 40, y: 60, step: 1, label: 'POST /auth/login', type: 'base' },
  { id: 'node2', x: 200, y: 120, step: 2, label: 'GET /user/profile', type: 'active', context: 'Auth_Token passed ✓' },
  { id: 'node3', x: 60, y: 200, step: 3, label: 'POST /cart/add', type: 'base' },
  { id: 'node4', x: 220, y: 260, step: 4, label: 'POST /checkout', type: 'base' }
])

const draggingNode = ref(null)
const offset = ref({ x: 0, y: 0 })

function handleDragStart(e, nodeId) {
  e.preventDefault()
  draggingNode.value = nodeId
  const target = nodes.value.find(n => n.id === nodeId)
  if (!target) return
  
  // Handle both touch and mouse events
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  
  offset.value = {
    x: clientX - target.x,
    y: clientY - target.y
  }
}

function handleDragMove(e) {
  if (!draggingNode.value) return
  const target = nodes.value.find(n => n.id === draggingNode.value)
  if (!target) return
  
  // Handle both touch and mouse events
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  
  target.x = clientX - offset.value.x
  target.y = clientY - offset.value.y
}

function handleDragEnd() {
  draggingNode.value = null
}

// Video Player State
const demoVideo = ref(null)
const progressBar = ref(null)
const videoLoading = ref(true)
const videoBuffering = ref(false)
const videoPlaying = ref(false)
const videoMuted = ref(false)
const videoProgress = ref(0)
const currentTime = ref(0)
const duration = ref(0)

// Aggressively cache the demo video using Cache API
const VIDEO_URL = '/Specflow recroding.mp4'
const CACHE_NAME = 'specflow-video-cache-v1'

async function cacheVideo() {
  if ('caches' in window) {
    try {
      // Open or create the cache
      const cache = await caches.open(CACHE_NAME)
      
      // Check if already cached
      const cachedResponse = await cache.match(VIDEO_URL)
      if (cachedResponse) {
        console.log('Video already cached')
        return
      }
      
      // Fetch and cache the video
      console.log('Caching video...')
      const response = await fetch(VIDEO_URL, { mode: 'cors' })
      
      if (response.ok) {
        await cache.put(VIDEO_URL, response.clone())
        console.log('Video cached successfully')
      }
    } catch (error) {
      console.log('Video caching skipped:', error.message)
    }
  }
}

// Preload video from cache if available
async function preloadVideoFromCache() {
  if ('caches' in window) {
    try {
      const cache = await caches.open(CACHE_NAME)
      const cachedResponse = await cache.match(VIDEO_URL)
      
      if (cachedResponse) {
        console.log('Video found in cache, using cached version')
        // Create a blob URL from the cached response
        const blob = await cachedResponse.blob()
        const cachedUrl = URL.createObjectURL(blob)
        
        // Update the video source if element exists
        if (demoVideo.value) {
          demoVideo.value.src = cachedUrl
          demoVideo.value.load()
        }
      } else {
        // Cache for next time
        cacheVideo()
      }
    } catch (error) {
      console.log('Video preload skipped:', error.message)
    }
  }
}

// Run on mount
onMounted(() => {
  preloadVideoFromCache()
})

function handleVideoLoadStart() {
  videoLoading.value = true
  videoProgress.value = 0
}

function handleVideoLoaded() {
  videoLoading.value = false
  if (demoVideo.value) {
    duration.value = demoVideo.value.duration
  }
}

function handleVideoEnded() {
  videoPlaying.value = false
  videoProgress.value = 0
  if (demoVideo.value) {
    demoVideo.value.currentTime = 0
  }
}

function handleTimeUpdate() {
  if (!demoVideo.value) return
  currentTime.value = demoVideo.value.currentTime
  videoProgress.value = (demoVideo.value.currentTime / demoVideo.value.duration) * 100
}

function togglePlay() {
  if (!demoVideo.value) return
  if (videoPlaying.value) {
    demoVideo.value.pause()
    videoPlaying.value = false
  } else {
    demoVideo.value.play()
    videoPlaying.value = true
  }
}

function toggleMute() {
  if (!demoVideo.value) return
  demoVideo.value.muted = !demoVideo.value.muted
  videoMuted.value = demoVideo.value.muted
}

function toggleFullscreen() {
  if (!demoVideo.value) return
  if (demoVideo.value.requestFullscreen) {
    demoVideo.value.requestFullscreen()
  } else if (demoVideo.value.webkitRequestFullscreen) {
    demoVideo.value.webkitRequestFullscreen()
  }
}

function seekVideo(event) {
  if (!demoVideo.value || !progressBar.value) return
  const rect = progressBar.value.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = clickX / rect.width
  demoVideo.value.currentTime = percentage * demoVideo.value.duration
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.card-feature {
  padding: 2rem;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  transition: all 0.3s ease;
}

.card-feature:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-0.25rem);
}

@keyframes drawUnderline {
  from { stroke-dashoffset: 350; }
  to { stroke-dashoffset: 0; }
}

.underline-path {
  stroke-dasharray: 350;
  stroke-dashoffset: 350;
  animation: drawUnderline 1.2s cubic-bezier(0.65, 0, 0.35, 1) forwards;
  animation-delay: 0.5s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes scan {
  from { transform: translateY(-100%); }
  to { transform: translateY(400%); }
}

@keyframes flow-down {
  0% { top: 0%; opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

@keyframes drop {
  0% { transform: translateY(0); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(20px); opacity: 0; }
}

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-spin-slow {
  animation: spin-slow 12s linear infinite;
}

.animate-flow-down {
  animation: flow-down 1s linear infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 2s ease-in-out infinite;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: black;
}
::-webkit-scrollbar-thumb {
  background: #1a1a1a;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #2a2a2a;
}
</style>
