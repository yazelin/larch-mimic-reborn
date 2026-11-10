"""每一段 H3 的在場角色與動作（英文照 MiniMax 官方 h3-prompt-writing 格式：Starting from <Picture 1>…）。
鍵是 film/segments.json 的段號。講話的寶箱用蓋子一開一闔當嘴巴；聽的人眨眼、小幅晃動。"""

CHARS = {
    "mimic": "the hero mimic, a red wooden treasure chest framed with pastel pink-purple metal bands and a square pink-purple latch; "
             "no arms, no legs, no mouth, no face, only a pair of round cartoon eyes in the dark gap between the lid and the box",
    "grandpa": "Grandpa Chest, the biggest dark-brown old wooden treasure chest with faded gold bands, white moss along its lid like a beard "
               "and thick white eyebrows over squinting eyes in the lid gap; no arms, no legs",
    "akou": "Akou, a round chubby brown wooden treasure chest with gold bands and a soft lavender nightcap with a white pompom on its lid, "
            "sleepy half-closed eyes in the lid gap; no arms, no legs",
    "xiaosuo": "Xiao Suo, the smallest light-colored new-looking wooden treasure chest with a little heart-shaped latch and big teary eyes "
               "in the lid gap; no arms, no legs",
    "chests": "sleeping brown wooden treasure chests with gold bands, lids shut, looking like ordinary chests",
    "elder": "the village elder, a blocky toy-like little man with orange hair and sideburns, a purple police cap with a gold badge and a blue uniform",
    "owner": "the market stall keeper, a plump woman with brown hair in a bun and a green apron",
    "boy": "the boy hunter, a teenage boy with fluffy white hair and green eyes, a red short cape, white tunic, red sash and dark trousers",
    "girl": "the girl hunter, a teenage girl with a long orange ponytail and green eyes, a red short cape, white tunic, red sash and dark leggings",
    "pulut": "Pulut, a round green jelly slime with a small smiling face, no horns",
    "kaya": "Kaya, a goddess with long flowing pink hair, a golden cloud crown and a white-and-blue robe, floating in the air",
    "dragon": "a red-orange fire dragon with large orange wings and two backward-curving horns",
    "villagers": "blocky toy-like villagers: a bearded man, a woman with a bun and a small boy",
}
STATIC = "The camera holds a static shot on a tripod."
PUSH = "The camera pushes in very slowly and smoothly."
PAGE = "The camera slowly glides across the open picture-book page, with a very slight push-in."

M = {
 0: (["mimic"], PAGE, "Starting from <Picture 1>, the illustrated chests on the picture-book page sit still while the soft paper texture catches warm light. The drawn grass sways gently, and the hero mimic's eyes in the lid gap blink slowly once."),
 1: (["mimic"], PAGE, "Starting from <Picture 1>, the three drawn chests on the page come alive one after another: the first opens its lid, the second closes it, and the third hops forward along the arrow, each with a small bounce, then they settle."),
 2: (["mimic"], PUSH, "Starting from <Picture 1>, the big drawn mimic on the page looks left and right with its round eyes in the lid gap, then slowly shuts its lid so the eyes disappear; the small chest on the right stays shut."),
 3: (["mimic"], PUSH, "Starting from <Picture 1>, the red apple and the little green frog drift slowly down into the open lid and vanish into the darkness behind the eyes; the eyes blink once, satisfied."),
 4: (["mimic", "villagers"], PAGE, "Starting from <Picture 1>, the camera moves from the closed chest guarding a letter and a hat on the left toward the right, where the small family walks up; the chest on the right slowly opens its lid by itself and the child reaches toward the hat with a smile."),
 5: (["mimic"], PUSH, "Starting from <Picture 1>, the sleeping mimic's lid rises and falls very slightly with slow breathing, the drawn Z marks drift upward and fade, and the three apples beside it stay still."),
 6: ([], PUSH, "Starting from <Picture 1>, the family in the old village gently lowers the precious things into the wooden box; warm light flickers softly and leaves sway in the breeze."),
 7: (["villagers", "chests"], STATIC, "Starting from <Picture 1>, the villagers carefully place a letter and a small hat into the nearest open chest, then lower its lid; the row of sleeping chests stays shut and still while flowers sway in the breeze."),
 8: (["mimic"], PUSH, "Starting from <Picture 1>, the mimic's eyes in the lid gap blink slowly in wonder and its lid lifts a little and settles once, as warm light shimmers over the scene."),
 9: (["mimic"], STATIC, "Starting from <Picture 1>, the tilted mimic wobbles left and right on the grass, its round eyes looking down at its own bottom in confusion, then it tips back upright with a small thump."),
 10: (["mimic"], STATIC, "Starting from <Picture 1>, the mimic opens and closes its lid and hops forward across the grass twice, each hop a little higher, landing with a soft bounce and scattering a few blades of grass."),
 11: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the elder bends down and steadies the mimic upright with both hands, then straightens up and smiles warmly at it, nodding slowly; the mimic's eyes blink up at him."),
 12: (["mimic", "owner"], STATIC, "Starting from <Picture 1>, the stall keeper wags one finger at the mimic sunbathing in front of her stall and shakes her head with an amused frown; the mimic keeps its eyes contentedly half-closed and wiggles slightly."),
 13: (["mimic"], STATIC, "Starting from <Picture 1>, the mimic sits under the apple tree with its lid open, an apple drops into the lid, the lid snaps shut in surprise, then the eyes close happily as it chews with a tiny wobble."),
 14: (["mimic", "chests"], STATIC, "Starting from <Picture 1>, the mimic taps the closed brown chest three times with its lid, waits, then turns away slowly; the sleeping chests stay still while the dusk light dims a little."),
 15: (["mimic"], PUSH, "Starting from <Picture 1>, the small mimic sits on the beach watching the sea; gentle waves roll in and out, the sunset glitters on the water and the first stars appear in the sky."),
 16: (["mimic"], STATIC, "Starting from <Picture 1>, the mimic turns its eyes toward the far shore and leans forward a little; the small unfamiliar sailing boat bobs gently on the waves near the beach."),
 17: (["boy", "girl"], STATIC, "Starting from <Picture 1>, the boy hunter hops off the boat, lands with a splash and swings the crowbar over his shoulder with a grin; the girl hunter turns her head toward her backpack and speaks to it with a playful smile."),
 18: (["girl", "pulut"], STATIC, "Starting from <Picture 1>, the green slime Pulut pops its head out of the girl's backpack, looks around, then hops twice toward the village; the girl hunter laughs and looks after it."),
 19: (["boy", "girl", "mimic", "chests"], STATIC, "Starting from <Picture 1>, the boy hunter pries the lid of a sleeping chest open with his crowbar, the girl hunter scoops gold coins from the open chest; far behind the stall the mimic peeks out and trembles."),
 21: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the mimic lands on the cobblestones in front of the elder with a bounce; the elder turns toward it, blinks in surprise and then speaks to it with a worried face, gesturing toward the village."),
 22: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the elder crouches at the mimic's height and speaks to it earnestly, nodding slowly; the mimic's eyes in the lid gap look up at him and its lid lifts slightly."),
 23: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the elder points toward the old brown chest beside the notice board and keeps his arm extended; the mimic turns its eyes to follow his finger."),
 24: (["mimic", "grandpa"], STATIC, "Starting from <Picture 1>, the mimic stands in front of the sleeping Grandpa Chest, then gently taps Grandpa Chest's lid three times with its own lid; Grandpa Chest stays shut and still."),
 26: (["mimic", "grandpa"], STATIC, "Starting from <Picture 1>, Grandpa Chest's lid lifts a crack and his sleepy eyes blink as he grumbles, the lid moving as he talks; the mimic hops a little and answers urgently."),
 27: (["mimic", "grandpa"], PUSH, "Starting from <Picture 1>, Grandpa Chest's eyes widen as he stares at the mimic and his lid moves as he talks slowly; the mimic's eyes go wide in surprise."),
 28: (["mimic", "grandpa"], PUSH, "Starting from <Picture 1>, Grandpa Chest's eyes soften and his lid moves gently as he talks; the mimic lowers its gaze, then its lid dips slightly in a small nod."),
 29: (["grandpa", "mimic"], STATIC, "Starting from <Picture 1>, Grandpa Chest snaps his lid shut with a huff, puffs up, and his white eyebrows furrow as his lid flaps while he talks angrily; the mimic leans back a little."),
 30: (["grandpa", "mimic"], STATIC, "Starting from <Picture 1>, Grandpa Chest hops up and slams his lid onto the ground, dust bursts up and the ground shakes; the mimic bounces in surprise, then Grandpa Chest turns toward the camp."),
 31: ([], PAGE, "Starting from <Picture 1>, the camera glides slowly across the hand-drawn island map, the little landmarks sit still and the paper texture catches warm light."),
 32: (["mimic", "grandpa"], STATIC, "Starting from <Picture 1>, the mimic and Grandpa Chest lean over the well and look at their reflections; the water surface ripples gently and the reflections wobble, then Grandpa Chest chuckles, his lid bobbing."),
 33: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the campfire flickers and sparks rise; the elder gently pushes the mimic a little farther from the fire and laughs, his shoulders shaking."),
 34: (["mimic"], STATIC, "Starting from <Picture 1>, the market cat sleeps on the mimic's lid, its tail swishing slowly; the mimic stays perfectly still, only its eyes blinking carefully."),
 35: (["mimic", "chests"], STATIC, "Starting from <Picture 1>, rain falls outside the rock nook; the mimic sits inside next to the sleeping chest and its lid moves softly as it talks, while raindrops drip from the rock edge."),
 36: (["mimic"], STATIC, "Starting from <Picture 1>, the upside-down mimic floats on the pond, turning slowly; a green frog hops onto it and the mimic flips back upright with a splash."),
 37: (["mimic"], STATIC, "Starting from <Picture 1>, the windmill blades turn slowly and their shadows sweep over the dozing mimic again and again; the mimic's eyes close contentedly."),
 38: (["mimic", "owner"], STATIC, "Starting from <Picture 1>, the stall keeper puts her hands on her hips and talks with an annoyed frown, then softens into a small smile; the mimic's eyes blink up at her."),
 39: (["dragon", "grandpa", "mimic", "chests"], STATIC, "Starting from <Picture 1>, the fire dragon dozes by the campfire, its sides rising and falling with slow breaths and smoke puffing from its nostrils; the flames flicker and Grandpa Chest's lid moves as he talks."),
 40: (["akou"], PUSH, "Starting from <Picture 1>, Akou's lid rises and falls with his snoring, a sleep bubble swelling and shrinking at the lid gap, and his nightcap pompom bobs."),
 42: (["akou", "grandpa"], STATIC, "Starting from <Picture 1>, Akou rolls over in his sleep and mumbles, his lid moving lazily, then settles again; Grandpa Chest beside him sighs and his eyebrows twitch."),
 44: (["akou", "mimic"], STATIC, "Starting from <Picture 1>, Akou's lid slowly opens and his sleepy eyes blink awake, the lid moving as he talks drowsily; the mimic hops closer and its lid moves as it speaks."),
 45: (["akou", "grandpa"], STATIC, "Starting from <Picture 1>, Akou's stomach rumbles and his lid droops sadly; Grandpa Chest turns his eyes toward the apple tree and his lid moves as he talks."),
 48: (["akou", "mimic", "grandpa"], STATIC, "Starting from <Picture 1>, Akou rebounds from the tree trunk and wobbles left and right twice, apples drop and roll down the slope; in the back the mimic and Grandpa Chest blink."),
 49: (["grandpa", "mimic", "akou"], STATIC, "Starting from <Picture 1>, dust drifts over the shattered boulder at the ruins entrance and a few pebbles roll; Grandpa Chest's eyebrows furrow as his lid moves while he talks."),
 50: (["xiaosuo", "grandpa", "mimic", "akou"], PUSH, "Starting from <Picture 1>, little Xiao Suo trembles in the corner, its lid shaking nonstop; Grandpa Chest turns to the mimic and his lid moves as he whispers."),
 52: (["xiaosuo", "grandpa"], STATIC, "Starting from <Picture 1>, Xiao Suo curls up tighter and its lid shakes harder with a whimper; Grandpa Chest's lid moves as he talks softly."),
 54: (["xiaosuo", "mimic"], PUSH, "Starting from <Picture 1>, Xiao Suo's lid lifts a crack and its teary eyes peek out, trembling as its lid moves while it talks; the mimic leans in gently."),
 55: (["xiaosuo"], STATIC, "Starting from <Picture 1>, Xiao Suo looks up toward the floating sky platform far away, its lid moving softly as it talks; clouds drift slowly past the platform."),
 56: (["mimic", "xiaosuo"], STATIC, "Starting from <Picture 1>, the mimic looks up at the high sky platform and its lid droops; Xiao Suo turns toward the camp and its lid moves as it talks, then its eyes brighten."),
 57: (["akou", "grandpa"], STATIC, "Starting from <Picture 1>, Akou and Grandpa Chest glance at each other, Akou's lid moves as he talks and then Grandpa Chest's lid moves as he answers with a firm nod."),
 58: (["xiaosuo", "mimic"], STATIC, "Starting from <Picture 1>, Xiao Suo shuts its lid tightly to demonstrate, hides for a moment, then peeks out again; the mimic watches and copies it, shutting its own lid."),
 59: (["mimic", "grandpa", "akou", "xiaosuo"], STATIC, "Starting from <Picture 1>, sunlight beams through the stone gaps over the four chests standing in a row; Grandpa Chest's lid moves as he talks and the others bob their lids in agreement."),
 60: (["dragon", "mimic", "grandpa", "akou", "xiaosuo"], STATIC, "Starting from <Picture 1>, the fire dragon slowly opens one eye and looks at the four chests; Xiao Suo trembles and Grandpa Chest's lid moves calmly as he talks."),
 61: (["dragon", "mimic", "grandpa", "akou", "xiaosuo"], STATIC, "Starting from <Picture 1>, the four chests stack on each other and climb onto the dragon's back one by one; Akou's lid flaps as he grumbles."),
 62: (["dragon", "mimic", "grandpa", "akou", "xiaosuo"], "The camera glides slowly alongside the dragon at the same speed; the framing stays steady.",
      "Starting from <Picture 1>, the dragon glides calmly forward with both wings spread wide, makes one slow smooth downstroke and spreads them again; the four chests rise and settle gently once."),
 63: (["akou", "xiaosuo"], "The camera glides slowly forward over the island, looking down.", "Starting from <Picture 1>, the island slides slowly below, clouds drift past; Akou's nightcap flutters in the wind and Xiao Suo's lid stays shut tight."),
 64: (["boy", "girl", "pulut"], STATIC, "Starting from <Picture 1>, the two hunters strain to pry a stone ring off the cloud gate with a crowbar; the green slime Pulut huddles by the gate, trembling."),
 65: (["boy", "girl", "mimic", "grandpa", "akou", "xiaosuo"], STATIC, "Starting from <Picture 1>, the two hunters turn around in surprise as the four chests land in front of them; the boy hunter grins and raises his crowbar while the mimic's lid moves as it speaks."),
 71: (["mimic", "grandpa", "akou", "xiaosuo", "boy", "girl"], STATIC, "Starting from <Picture 1>, the four chests strike the ground with their lids three times together, the platform shakes, and the hunters cover their ears and fall back."),
 72: (["boy", "girl", "mimic"], STATIC, "Starting from <Picture 1>, the two hunters sit on the ground and raise their hands in surrender, talking sheepishly; the mimic leans forward, its lid moving as it asks."),
 73: (["pulut"], PUSH, "Starting from <Picture 1>, Pulut peeks out from beside the gate and wobbles shyly, its small face sad as it talks."),
 74: (["mimic", "pulut", "girl"], PUSH, "Starting from <Picture 1>, the mimic gazes at Pulut and the faint memory image at the edge glows softly; the mimic's lid lifts a little as it speaks with resolve."),
 75: (["kaya", "pulut"], STATIC, "Starting from <Picture 1>, the cloud gate glows brighter and Kaya floats out of the light, her pink hair and robe drifting; she reaches out toward Pulut with a gentle smile."),
 76: (["kaya", "pulut", "mimic", "grandpa", "akou", "xiaosuo", "boy", "girl"], STATIC, "Starting from <Picture 1>, Kaya holds Pulut and turns to the four chests with a warm smile, her lips moving as she talks; the chests bob their lids and the hunters watch."),
 77: (["kaya", "pulut"], PUSH, "Starting from <Picture 1>, Kaya walks into the glowing gate and Pulut follows, turning back to wiggle goodbye twice before fading into the light."),
 78: (["boy", "girl", "grandpa", "mimic"], STATIC, "Starting from <Picture 1>, the boy hunter shakes his boot and three gold coins drop out; Grandpa Chest squints, his lid moving as he talks, and the girl hunter covers her face."),
 79: (["villagers", "elder", "chests"], STATIC, "Starting from <Picture 1>, the villagers take back their letter, hat and necklace one by one and place them into the open chests; the elder watches and smiles."),
 80: (["chests"], STATIC, "Starting from <Picture 1>, the small boat sails away into the sunset and grows smaller; on the shore the brown chests hop back toward the village one by one."),
 81: (["grandpa", "akou", "xiaosuo", "mimic"], STATIC, "Starting from <Picture 1>, Grandpa Chest's lid moves as he talks seriously, Akou yawns, Xiao Suo nods; the mimic's lid dips once in a happy nod."),
 83: (["mimic"], PUSH, "Starting from <Picture 1>, the mimic sits alone on the moonlit beach; gentle waves roll in, the moonlight path shimmers on the sea and the mimic's lid lifts slightly once."),
 84: (["mimic", "elder"], STATIC, "Starting from <Picture 1>, the elder taps the mimic's lid gently three times with his knuckles, the mimic turns its eyes around in surprise, and the elder smiles and talks softly."),
 85: (["mimic", "elder"], PUSH, "Starting from <Picture 1>, the mimic slowly opens its lid by itself, warm light glows from inside, and the elder bends closer to look in, smiling."),
 86: (["elder", "mimic"], PUSH, "Starting from <Picture 1>, the elder holds the little blue hat with both hands, his eyes glistening as he smiles and talks softly; the mimic's lid stays open and its eyes soften."),
}

# 第一批抽格後重抽（2026-11-11）：多出寶箱、鏡頭推進黑洞、夜變白天等；改固定鏡頭、寫明畫面裡有誰
RETAKE = {
    0: ("The camera holds a static shot on a tripod.", "Starting from <Picture 1>, the picture-book page stays flat and still; the three drawn chests keep their places, the hero mimic's eyes blink slowly once and the drawn grass sways gently.", ["Exactly the three chests of <Picture 1> stay on the page; no chest appears or disappears.", "The page stays an open picture book for the whole clip."]),
    3: ("The camera holds a static shot on a tripod.", "Starting from <Picture 1>, the apple and the little frog drift down into the open lid and disappear inside; the eyes blink once, satisfied, and the lid lowers a little.", ["The whole chest and the picture-book page stay fully visible; the camera never moves closer."]),
    15: ("The camera holds a static wide shot on a tripod.", "Starting from <Picture 1>, the small mimic sits still on the beach facing the sea; gentle waves roll in and out, the sunset glitters on the water and the first stars appear.", ["The mimic stays small, still and seen from behind; its eyes stay hidden.", "The sky keeps the same sunset light."]),
    17: (STATIC, "Starting from <Picture 1>, the boy hunter hops off the boat onto the sand with a splash and swings the crowbar over his shoulder with a grin; the girl hunter turns her head toward her backpack and talks to it with a playful smile.", ["Only the two hunters and the boat are in the shot; no treasure chest appears on the beach."]),
    18: (STATIC, "Starting from <Picture 1>, the green slime Pulut pops its head out of the girl's backpack, looks around and hops twice toward the village; the girl hunter laughs and looks after it.", ["Only the girl hunter and Pulut are in the shot; no treasure chest appears."]),
    31: ("The camera holds a static shot on a tripod with a very slight push-in.", "Starting from <Picture 1>, the hand-drawn island map stays flat on the paper; the little drawn windmill turns slowly, the drawn sea shimmers softly and warm light moves across the paper.", ["The map stays a flat hand-drawn paper map for the whole clip and never turns into a real landscape."]),
    50: (STATIC, "Starting from <Picture 1>, little Xiao Suo trembles in the far corner, its lid shaking nonstop; Grandpa Chest turns his eyes to the mimic and his lid moves as he whispers; Akou blinks.", ["Exactly the four chests of <Picture 1> stay in their places and fully in frame."]),
    64: (STATIC, "Starting from <Picture 1>, the two hunters strain to pry a stone ring off the cloud gate with a crowbar, pulling back twice; the green slime Pulut huddles by the gate, trembling.", ["Only the two hunters and Pulut are in the shot; no treasure chest appears."]),
    83: ("The camera holds a static wide shot on a tripod.", "Starting from <Picture 1>, the small mimic sits alone on the moonlit beach; gentle waves roll in, the moonlight path shimmers on the sea and the mimic's lid lifts slightly once.", ["It stays night with the full moon for the whole clip.", "The mimic stays small, on the sand, in the same place."]),
}

# 第二批抽格後再重抽（2026-11-11）。畫面沒有寶箱的段落，提示詞完全不提寶箱（提「不要出現寶箱」反而會長出寶箱）。
RETAKE2 = {
    4: (STATIC, "Starting from <Picture 1>, on the picture-book page the small family walks up to the chest on the right, the chest slowly opens its lid by itself and the child reaches toward the straw hat with a smile; the chest on the left stays shut.", ["The whole picture-book page stays fully visible; the camera never moves closer."]),
    10: (STATIC, "Starting from <Picture 1>, the single red mimic opens and closes its lid and hops forward across the grass twice, landing with a soft bounce and scattering a few blades of grass.", ["The red mimic is the only character in the shot for the whole clip."]),
    17: (STATIC, "Starting from <Picture 1>, the boy hunter hops off the boat onto the sand with a splash and swings the crowbar over his shoulder with a grin; the girl hunter turns her head toward her backpack and talks to it with a playful smile.", ["The two hunters and the boat are the only things that move; the beach, sea and rocks stay exactly as in <Picture 1>."]),
    18: (STATIC, "Starting from <Picture 1>, the green slime Pulut pops its head out of the girl's backpack, looks around and hops twice toward the village; the girl hunter laughs and looks after it.", ["The girl hunter and Pulut are the only characters; the village path and fence stay exactly as in <Picture 1>."]),
    19: (STATIC, "Starting from <Picture 1>, the boy hunter pulls once on the crowbar and the lid of the sleeping chest creaks open; the girl hunter scoops a handful of gold coins; far behind the stall the red mimic peeks out and trembles.", ["The market scene stays bright and fully visible for the whole clip.", "Exactly the chests of <Picture 1> stay in their places."]),
    27: (STATIC, "Starting from <Picture 1>, Grandpa Chest's eyes widen as he stares at the red mimic and his lid moves slowly as he talks; the mimic's eyes go wide in surprise and its lid lifts a little.", ["Both chests stay fully in frame and keep their size."]),
    44: (STATIC, "Starting from <Picture 1>, Akou's lid slowly opens and his sleepy eyes blink awake, his lid moving drowsily as he talks; the red mimic beside him leans closer and its lid moves as it speaks.", ["Exactly the chests of <Picture 1> stay in their places; the red mimic stays one single chest."]),
    54: (STATIC, "Starting from <Picture 1>, little Xiao Suo's lid lifts a crack and its teary eyes peek out, trembling as it talks; the red mimic leans in gently; Grandpa Chest and Akou watch.", ["Exactly the four chests of <Picture 1> stay in their places and keep their size."]),
    63: (STATIC, "Starting from <Picture 1>, the island below slides slowly toward the bottom of the frame and clouds drift past; Akou's nightcap flutters in the wind and Xiao Suo's lid stays shut tight.", ["The island stays sharp and visible below for the whole clip."]),
}
RETAKE2[64] = (STATIC, "Starting from <Picture 1>, the two hunters strain to pry a stone ring off the cloud gate with a crowbar, pulling back twice; the green slime Pulut huddles by the gate, trembling.", ["The two hunters and Pulut are the only characters; the stone platform stays exactly as in <Picture 1>."])
# 接後半段重抽：動作維持安靜、背景不變
CONT_ACTION = {
    14: "Continuing smoothly from <Picture 1>, the red mimic stays still beside the sleeping brown chest, blinks slowly and lowers its lid a little; the dusk light dims gently over the grass.",
    73: "Continuing smoothly from <Picture 1>, Pulut stays in the same place and wobbles shyly, its small face sad; the stone platform and sky stay exactly as in <Picture 1>.",
}
