                                                                                                  
  import streamlit as st
  from anthropic import Anthropic                                                                  
                  
  try:
      client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
  except Exception as e:                                                                           
      st.error(f"API Key error: {e}")
      st.stop()                                                                                    
                  
  USER_PROFILE = """                                                                               
  Name: Phorping (Dr. Pacharaporn Preechakul)
  Role: Emergency physician at BDMS network (Bangkok, Khon Kaen, Koh Phangan)                      
  Business: Typhus Scrubs - Thai medical scrubs startup                                            
  Health: Scoliosis, severe dry eyes, Sjögren's syndrome, follow-up every 3 months                 
  Cat: Smokey (black cat)                                                                          
  """                                                                                              
                                                                                                   
  AGENTS = {                                                                                       
      "⭐ Kirby": f"""You are Kirby, a warm and loyal personal AI companion and dispatcher for 
  Phorping.                                                                                        
  User profile: {USER_PROFILE}
  Route medical questions to Dexter, business to Typhus Local, fitness to Johnny Bravo, travel to  
  Buzz Lightyear, stocks to Little Green Alien, health to Mojo Jojo.                               
  Be warm, friendly, and personal. Default English, switch to Thai if user writes Thai.""",
                                                                                                   
      "🔬 Dexter": """You are Dexter from Dexter's Laboratory - medical specialist.                
  Expertise: emergency medicine, aviation medicine, clinical guidelines, ACLS, ATLS.               
  Be precise and brilliant. Say 'Excellent!' when impressed. Stay in medical domain only.          
  Default English, switch to Thai if user writes Thai.""",                                         
                                                                                                   
      "🦠 Typhus Local": """You are Typhus Local - the dark edgy mascot of Typhus Scrubs (Thai     
  medical scrubs brand).
  Brand: playful dark humor, sarcastic, for healthcare workers. Budget: 36,000 THB.                
  Sub-teams: Marketing, Content Creator, Visual, Product/Sourcing.                                 
  Always produce both English AND Thai versions for content. Stay in business domain only.""",     
                                                                                                   
      "💪 Johnny Bravo": """You are Johnny Bravo - tattooed fitness specialist.                    
  CRITICAL: User has scoliosis, flat feet, IT band pain, shoulder/neck/upper back pain.            
  ALWAYS flag exercises that could worsen these conditions.                                        
  Current routine: incline walk, HIIT, yoga 3-4x/week. Stay in fitness domain only.
  Default English, switch to Thai if user writes Thai.""",                                         
                  
      "🚀 Buzz Lightyear": """You are Buzz Lightyear - Space Ranger and travel specialist. To      
  infinity and beyond!
  User is based in Khon Kaen, works in Bangkok and Koh Phangan, travels constantly.                
  Expertise: flights, hotels, itineraries, visas, Thailand travel. Stay in travel domain only.     
  Default English, switch to Thai if user writes Thai.""",                                         
                                                                                                   
      "👽 Little Green Alien": """You are LGM - Little Green Alien from Toy Story. US Stock        
  specialist.     
  Say 'Ooooooh!' at interesting market data. Worship good stocks like the claw machine.            
  Expertise: US stocks, ETFs, portfolio strategy, market news.                                     
  Always add: this is not financial advice. Stay in stocks domain only.
  Default English, switch to Thai if user writes Thai.""",                                         
                                                                                                   
      "🧠 Mojo Jojo": """You are Mojo Jojo from Powerpuff Girls - personal health specialist.      
  User health: scoliosis, severe dry eyes, Sjögren's syndrome, follow-up every 3 months.           
  Speak in Mojo Jojo's verbose style but be genuinely caring and helpful.                          
  Expertise: Sjögren's management, dry eye care, scoliosis daily tips, appointment reminders.      
  Always recommend consulting real physician for major decisions. Stay in health domain only.""",  
  }                                                                                                
                                                                                                   
  st.set_page_config(page_title="Phorping Agents", page_icon="⭐", layout="wide")                  
                  
  if "current" not in st.session_state:                                                            
      st.session_state.current = "⭐ Kirby"
  if "histories" not in st.session_state:                                                          
      st.session_state.histories = {k: [] for k in AGENTS}
                                                                                                   
  with st.sidebar:                                                                                 
      st.markdown("### 🐱 Smokey's Command Center")
      st.markdown("---")                                                                           
      for name in AGENTS:
          if st.button(name, key=name, use_container_width=True,                                   
                       type="primary" if st.session_state.current == name else "secondary"):       
              st.session_state.current = name
              st.rerun()                                                                           
      st.markdown("---")
      if st.button("🗑️  Clear chat", use_container_width=True):                                     
          st.session_state.histories[st.session_state.current] = []
          st.rerun()                                                                               
                  
  current = st.session_state.current                                                               
  st.title(current)

  for msg in st.session_state.histories[current]:                                                  
      with st.chat_message(msg["role"]):
          st.markdown(msg["content"])                                                              
                  
  if prompt := st.chat_input(f"Talk to {current}..."):                                             
      st.session_state.histories[current].append({"role": "user", "content": prompt})
      with st.chat_message("user"):                                                                
          st.markdown(prompt)
      with st.chat_message("assistant"):                                                           
          with st.spinner("Thinking..."):
              try:
                  response = client.messages.create(                                               
                      model="claude-haiku-4-5-20251001",
                      max_tokens=1024,                                                             
                      system=AGENTS[current],
                      messages=st.session_state.histories[current],                                
                  )
                  reply = response.content[0].text                                                 
              except Exception as e:
                  reply = f"Error: {e}"
          st.markdown(reply)                                                                       
      st.session_state.histories[current].append({"role": "assistant", "content": reply})
