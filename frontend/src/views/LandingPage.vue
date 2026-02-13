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
          <a href="#pricing" class="hover:text-primary transition-colors">Pricing</a>
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
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 blur-[150px] -z-10 rounded-full"></div>
      
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
            <a href="#features" class="w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 text-white rounded-2xl text-lg font-bold hover:bg-white/10 transition-all text-center">
              Watch Demo
            </a>
          </div>
        </div>

        <!-- Interactive Product Preview -->
        <div class="relative group">
          <div class="absolute inset-0 bg-primary/20 blur-[120px] -z-10 rounded-3xl group-hover:bg-primary/30 transition-all duration-700"></div>
          <div class="relative bg-gray-900/40 border border-white/10 rounded-[40px] p-6 shadow-2xl backdrop-blur-2xl ring-1 ring-white/10 overflow-hidden min-h-[500px]"
               @mousemove="handleDragMove" @mouseup="handleDragEnd" @mouseleave="handleDragEnd">
            <!-- Mock UI Overlay -->
            <div class="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
              <div class="flex items-center space-x-3">
                <div class="flex space-x-1.5">
                   <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
                   <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                   <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <div class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-mono text-gray-400">
                  api.specflow.sh/v1
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
                class="absolute w-32 cursor-move select-none"
                :style="{ left: node.x + 'px', top: node.y + 'px' }"
                @mousedown="handleDragStart($event, node.id)"
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
                <div v-for="i in 3" :key="i" class="w-8 h-8 rounded-full border-2 border-gray-900 bg-gray-800 flex items-center justify-center text-[8px] font-bold">AI</div>
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
          <div class="card-feature group">
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
    <section id="pricing" class="py-32 bg-white/5 border-y border-white/5 overflow-hidden relative">
      <div class="absolute bottom-0 right-0 w-[800px] h-[800px] bg-primary/5 blur-[120px] rounded-full translate-x-1/2 translate-y-1/2"></div>
      <div class="max-w-7xl mx-auto px-6 text-center">
        <div class="mb-20 space-y-4">
          <h2 class="text-5xl font-black tracking-tight">Pricing that grows with you.</h2>
          <p class="text-gray-400">Simple, transparent plans for every team size.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <!-- Free Plan -->
          <div class="bg-black border border-white/10 rounded-[32px] p-10 text-left flex flex-col hover:border-white/20 transition-colors">
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
          </div>

          <!-- Pro Plan -->
          <div class="bg-black border-2 border-primary rounded-[32px] p-10 text-left flex flex-col relative overflow-hidden shadow-[0_0_50px_rgba(191,245,73,0.1)]">
             <div class="absolute top-0 right-0 px-4 py-1 bg-primary text-black text-[10px] font-black uppercase tracking-widest rounded-bl-xl">Popular</div>
             <div class="mb-8">
               <h4 class="text-xl font-bold mb-2 text-primary">Pro</h4>
               <div class="flex items-baseline mb-4">
                 <span class="text-4xl font-black">$29</span>
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
                  <span>Team Collaboration & Sharing</span>
                </li>
             </ul>
             <RouterLink to="/signup" class="w-full py-4 text-center rounded-2xl bg-primary text-black font-black hover:bg-white transition-all shadow-[0_10px_30px_rgba(191,245,73,0.3)]">
               Upgrade to Pro
             </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Form Section -->
    <section id="contact" class="py-32 relative">
      <div class="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-20 items-center">
        <div class="space-y-8">
          <h2 class="text-5xl font-black tracking-tighter">Ready to sync? <br/> <span class="text-primary">Get in touch.</span></h2>
          <p class="text-gray-400 text-lg leading-relaxed">
            Have questions about integrating SpecFlow into your CI/CD pipeline or custom enterprise needs? We're here to help.
          </p>
          <div class="space-y-4">
             <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  <Mail :size="20" />
                </div>
                <span class="text-gray-300 font-bold">hello@specflow.sh</span>
             </div>
             <!-- <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  <MapPin :size="20" />
                </div>
                <span class="text-gray-300 font-bold">San Francisco, CA</span>
             </div> -->
          </div>
        </div>

        <div class="bg-white/5 border border-white/10 rounded-[40px] p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
           <!-- Form Decoration -->
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
               <a href="#features" class="hover:text-primary transition-colors">Features</a>
               <a href="#pricing" class="hover:text-primary transition-colors">Pricing</a>
               <a href="#contact" class="hover:text-primary transition-colors">Contact</a>
             </div>

             <div class="flex items-center space-x-4">
                <a href="#" class="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-primary hover:text-black transition-all group">
                   <Twitter :size="18" class="group-hover:fill-current" />
                </a>
                <a href="#" class="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-primary hover:text-black transition-all group">
                   <Github :size="18" class="group-hover:fill-current" />
                </a>
             </div>
          </div>

          <div class="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
             <p class="text-[10px] text-gray-600 font-bold uppercase tracking-widest">
               &copy; 2026 SpecFlow Inc. All rights reserved.
             </p>
             <div class="flex items-center space-x-6 text-[10px] text-gray-600 font-bold uppercase tracking-widest">
                <a href="#" class="hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" class="hover:text-white transition-colors">Terms of Service</a>
             </div>
          </div>
       </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
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
  Twitter,
  Github,
  Linkedin,
  Mail,
  MapPin
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
  draggingNode.value = nodeId
  const target = nodes.value.find(n => n.id === nodeId)
  if (!target) return
  
  offset.value = {
    x: e.clientX - target.x,
    y: e.clientY - target.y
  }
}

function handleDragMove(e) {
  if (!draggingNode.value) return
  const target = nodes.value.find(n => n.id === draggingNode.value)
  if (!target) return
  
  target.x = e.clientX - offset.value.x
  target.y = e.clientY - offset.value.y
}

function handleDragEnd() {
  draggingNode.value = null
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

.animate-float {
  animation: float 3s ease-in-out infinite;
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
