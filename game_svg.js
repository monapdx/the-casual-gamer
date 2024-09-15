// Copyright 2010-2015 Shy Gypsy, Inc.

// Cell dimensions, in pixels.
FF.CELLW = 640;
FF.CELLH = 480;

// Minimap dimensions, in pixels.
FF.MINIMAP_WIDTH = 210;
FF.MINIMAP_HEIGHT = 160;

FF.$ = function(id) {
    return document.getElementById(id);
};

/** Like document.createElement(), but uses the SVG namespace. **/
FF.MakeSvgNode = function(tag) {
  return document.createElementNS("http://www.w3.org/2000/svg", tag);
};

/** Like MakeSvgNode("image"). **/
FF.MakeSvgImageNode = function(url) {
  var img = FF.MakeSvgNode("image");
  img.setAttributeNS("http://www.w3.org/1999/xlink", "href", url);
  return img;
};

FF.BOLDIFY_REGEX = /<\/?b>/;

/** Renders a string with <b> tags in SVG. **/
FF.Boldify = function(s, node) {
  var arr = s.split(FF.BOLDIFY_REGEX);
  for (var i = 0; i < arr.length; ++i) if (arr[i]) {
    if (i % 2) {
      var tspan = FF.MakeSvgNode("tspan");
      tspan.setAttribute("style", "font-weight: bold");
      tspan.appendChild(document.createTextNode(arr[i]));
      node.appendChild(tspan);
    } else {
      node.appendChild(document.createTextNode(arr[i]));
    }
  }
};

/**
 * Append to 'svg' the SVG primitives that display vertex 'v'.
 **/
FF.AppendVertexElements = function(v, ccx, ccy, svg) {
  var vlabel = (v.dot_mask || v.name);
  var vclass = (v.dot_mask ? "uv" : "kv");
  if (v.kind == 4) vclass = "cv";
  var border = 3;
  var vx = v.rect.x - ccx - border / 2;  // SVG strokes are weird
  var vy = v.rect.y - ccy - border / 2;

  var rect = FF.MakeSvgNode("rect");
  rect.setAttribute("class", vclass);
  rect.setAttribute("x", vx);
  rect.setAttribute("y", vy);
  rect.setAttribute("width", v.rect.w + border);
  rect.setAttribute("height", v.rect.h + border);
  svg.appendChild(rect);

  var text = FF.MakeSvgNode("text");
  text.setAttribute("class", "ff-vertex-text");
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("x", v.center_x - ccx);
  text.setAttribute("y", v.center_y - ccy + 5);  // font-size: medium
  if (v.dot_mask) {
    FF.Boldify(vlabel, text);
  } else {
    text.appendChild(document.createTextNode(vlabel));
  }
  svg.appendChild(text);
};

/**
 * Paints the current cell.
 **/
FF.Paint = function(vertices) {
  // Build a map from vertex IDs to vertex objects.
  var vid2vertex = [];
  for (var i = 0; i < vertices.length; i++) {
    vid2vertex[vertices[i].vid] = vertices[i];
  }

  // Get the canvas and clear it.
  var svg = FF.$("main_svg");
  while (svg.lastChild) svg.removeChild(svg.lastChild);

  // Compute the offset of the cell's top-left corner.
  var ccx = FF.CELLW * FF.state.mmapi;
  var ccy = FF.CELLH * FF.state.mmapj;

  // Throw in the margin correction.
  var svg_w = +svg.getAttribute("width");
  var svg_h = +svg.getAttribute("height");
  ccx -= (svg_w - FF.CELLW) / 2;
  ccy -= (svg_h - FF.CELLH) / 2;

  // Draw the cell rectangle.
  var cellRect = FF.MakeSvgNode("rect");
  cellRect.setAttribute("class", "ff-cell");
  cellRect.setAttribute("x", (svg_w - FF.CELLW) / 2);
  cellRect.setAttribute("y", (svg_h - FF.CELLH) / 2);
  cellRect.setAttribute("width", FF.CELLW);
  cellRect.setAttribute("height", FF.CELLH);
  svg.appendChild(cellRect);

  // Draw edges.
  for (var i = 0; i < vertices.length; ++i) {
    var u = vertices[i];
    for (var c = 0; c < u.deg; ++c) {
      var v = vid2vertex[u.adj[c]];
      if (u.adj[c] >= u.vid || !v) continue;
      var line = FF.MakeSvgNode("line");
      line.setAttribute("class", "ff-edge");
      line.setAttribute("x1", u.center_x - ccx);
      line.setAttribute("y1", u.center_y - ccy);
      line.setAttribute("x2", v.center_x - ccx);
      line.setAttribute("y2", v.center_y - ccy);
      svg.appendChild(line);
    }
  }

  // Draw vertices.
  for (var i = 0; i < vertices.length; ++i) {
    FF.AppendVertexElements(vertices[i], ccx, ccy, svg);
  }
    
  // Have we just guessed a vertex?
  for (var i = 0; i < vertices.length; i++) {
    if (!vertices[i].dot_mask && FF.Paint.oldVertices &&
        FF.Paint.oldVertices[i].dot_mask) {
      // Shoot some fireworks in celebration.
      var vx = vertices[i].rect.x - ccx + v.rect.w / 2;
      var vy = vertices[i].rect.y - ccy + v.rect.h / 2;
      FF.StarShower(svg, vx, vy, 20);
      break;
    }
  }
  FF.Paint.oldVertices = vertices;
};

/**
 * 'state' is one of "no", "open", "solved".
 **/
FF.SetMetaPuzzleState = function(state) {
  var MSGS = {
    "no": "Not all meta-clues are unlocked.",
    "open": "<span style='color:red'>Meta-puzzle is unlocked!</span>",
    "solved": "Meta-puzzle is solved!"
  };
  var div = FF.$("meta-puzzle");
  var oldMsg = div.innerHTML;
  var newMsg = MSGS[state];
  if (!newMsg) {
    newMsg = "ERROR: GetMetaPuzzleState() returned " + state;
  }

  if (oldMsg == MSGS["open"] && newMsg == MSGS["solved"]) {
    FF.Fireworks(FF.$("main_svg"), 10, 20);
  }

  div.innerHTML = newMsg;
};

FF.PaintMinimap = function(minimap) {
  var svg = FF.$("minimap_svg");

  // Background.
  var bg = FF.MakeSvgNode("rect");
  bg.setAttribute("x", 0);
  bg.setAttribute("y", 0);
  bg.setAttribute("width", FF.MINIMAP_WIDTH + 3);
  bg.setAttribute("height", FF.MINIMAP_HEIGHT + 3);
  bg.setAttribute("class", "ff-minimap-grid");
  svg.appendChild(bg);

  // The minimap image.
  var img = FF.MakeSvgImageNode(FF.gameUrl + "/minimap.png");
  img.setAttribute("x", 1);
  img.setAttribute("y", 1);
  img.setAttribute("width", FF.MINIMAP_WIDTH);
  img.setAttribute("height", FF.MINIMAP_HEIGHT);
  img.onclick = FF.OnMinimapClick;
  svg.appendChild(img);

  // A mask for locked cells.
  for (var i = 0; i < FF.W; ++i) {
    for (var j = 0; j < FF.H; ++j) {
      if (!minimap[i][j]) {
        var rect = FF.MakeSvgNode("rect");
        rect.setAttribute("x", 2 + i * FF.CELL_WIDTH);
        rect.setAttribute("y", 2 + j * FF.CELL_HEIGHT);
        rect.setAttribute("width", FF.CELL_WIDTH - 1);
        rect.setAttribute("height", FF.CELL_HEIGHT - 1);
        rect.setAttribute("class", "ff-minimap-mask");
        svg.appendChild(rect);
      }
    }
  }

  // The grid.
  for (var x = 0; x < FF.MINIMAP_WIDTH; x += FF.CELL_WIDTH) {
    var rect = FF.MakeSvgNode("rect");
    rect.setAttribute("x", 1 + x);
    rect.setAttribute("y", 1);
    rect.setAttribute("width", 1);
    rect.setAttribute("height", FF.MINIMAP_HEIGHT);
    rect.setAttribute("class", "ff-minimap-grid");
    svg.appendChild(rect);
  }
  for (var y = 0; y < FF.MINIMAP_HEIGHT; y += FF.CELL_HEIGHT) {
    var rect = FF.MakeSvgNode("rect");
    rect.setAttribute("x", 1);
    rect.setAttribute("y", 1 + y);
    rect.setAttribute("width", FF.MINIMAP_WIDTH);
    rect.setAttribute("height", 1);
    rect.setAttribute("class", "ff-minimap-grid");
    svg.appendChild(rect);
  }

  // A frame around the current cell.
  if (minimap[FF.state.mmapi][FF.state.mmapj]) {
    var rect = FF.MakeSvgNode("rect");
    rect.setAttribute("x", 1 + FF.state.mmapi * FF.CELL_WIDTH);
    rect.setAttribute("y", 1 + FF.state.mmapj * FF.CELL_HEIGHT);
    rect.setAttribute("width", FF.CELL_WIDTH + 1);
    rect.setAttribute("height", FF.CELL_HEIGHT + 1);
    rect.setAttribute("class", "ff-minimap-frame");
    svg.appendChild(rect);
  }
};

/**
 * Called when the player clicks the minimap.
 **/
FF.OnMinimapClick = function(event) {
  var svgRect = FF.$("minimap_svg").getBoundingClientRect();
  var x = event.clientX - svgRect.left - 1;
  var y = event.clientY - svgRect.top - 1;
  var mmapi = Math.floor(x / FF.CELL_WIDTH);
  var mmapj = Math.floor(y / FF.CELL_HEIGHT);

  if (mmapi == FF.state.mmapi && mmapj == FF.state.mmapj) return;

  var svg = FF.$("main_svg");
  while (svg.lastChild) svg.removeChild(svg.lastChild);
  FF.Paint.oldVertices = null;

  AJAX.jsonRequest(
      FF.gameActionUrl, {"cmd": "MmapClick", "mmapi": mmapi, "mmapj": mmapj},
      function(response, code) {
        if (code != 200) {
          alert("Something went very wrong (code " + code + ")");
        } else if (response == "no") {
          alert("How did you manage to click that?");
        } else {
          FF.SetState(response);
        }
      },
      "POST"
  );
};

/**
 * Called when the player enters a guess and hits Enter.
 **/
FF.OnGuess = function() {
  var guess = FF.$("guess").value;
  FF.$("guess").value = "";

  AJAX.jsonRequest(
      FF.gameActionUrl, {"cmd": "Guess", "guess": guess},
      function(response, code) {
        if (code != 200) {
          alert("Something went very wrong (code " + code + ")");
        } else if (response == "no") {
          // Wrong guess. Do something?
        } else {
          FF.SetState(response);
        }
      },
      "POST"
  );
};

/**
 * Called whenever the game state changes, and we need to repaint.
 **/
FF.SetState = function(state) {
  FF.state = state;
  FF.SetCookie();
  FF.Paint(FF.state.vertices);
  FF.SetMetaPuzzleState(FF.state.meta);
  FF.PaintMinimap(FF.state.minimap);
};

/**
 * Updates the cookie to reflect the current game state.
 **/
FF.SetCookie = function() {
    // The cookie expires in a year.
    var date = new Date();
    date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000));

    document.cookie = [
        "g_", FF.gameId, "=",
        FF.state.estate, "&", FF.state.hstate, "&",
        FF.state.mmapi, "&", FF.state.mmapj,
        // FIXME: !!!!!
        ";domain=.funny-farm.appspot.com",
        ";host=localhost",
        ";expires=", date.toGMTString()
    ].join( "" );
};

/**
 * Calls 'drawFrame' many times during the next few 'seconds'.
 * When done, calls 'doneCallback'.
 */
FF.Animate = function(drawFrame, seconds, doneCallback) {
  var DELTA = 1 / 30;  // 30 FPS
  var now = 0;
  var render = function() {
    drawFrame(now);
    now += DELTA;
    if (now < seconds) {
      window.setTimeout(render, DELTA * 1000);
    } else {
      doneCallback();
    }
  };
  render();
};

/**
 * Fires off a shower of 'k' stars at (x, y) in 'svg'.
 */
FF.StarShower = function(svg, x, y, k) {
  // Create k stars at (x, y) with random speed vectors.
  var nodes = [];
  var positionX = [];
  var positionY = [];
  var velocityX = [];
  var velocityY = [];
  for (var i = 0; i < k; i++) {
    positionX[i] = x - 12;
    positionY[i] = y - 12;
    nodes[i] = FF.MakeSvgImageNode("/static/star.png");
    nodes[i].setAttribute("x", positionX[i]);
    nodes[i].setAttribute("y", positionY[i]);
    nodes[i].setAttribute("width", 24);
    nodes[i].setAttribute("height", 24);

    var angle = Math.sqrt(Math.random()) * Math.PI;
    var speed = 250 + Math.random() * 100;
    velocityX[i] = speed * Math.cos(angle);
    velocityY[i] = -speed * Math.sin(angle);

    svg.appendChild(nodes[i]);
  }

  // Animate the stars together.
  var lastTime = 0;
  FF.Animate(
    function(time) {
      // Compute new positions, velocities and opacities.
      var delta = time - lastTime;
      var friction = Math.pow(0.5, delta);
      var GRAVITY = 200.0;
      for (var i = 0; i < k; i++) {
        positionX[i] += velocityX[i] * delta;
        positionY[i] += velocityY[i] * delta;
        velocityX[i] *= friction;
        velocityY[i] *= friction;
        velocityY[i] += GRAVITY * delta;
        nodes[i].setAttribute("x", positionX[i]);
        nodes[i].setAttribute("y", positionY[i]);
        nodes[i].style.opacity = (2 - time) / 2;
      }
      lastTime = time;
    },
    2,
    function() {
      // Clean up.
      for (var i = 0; i < k; i++) {
        svg.removeChild(nodes[i]);
      }
    }
  );
};

/**
 * Fires off some fireworks in 'svg'.
 */
FF.Fireworks = function(svg, numShots, numShards) {
  for (var i = 0; i < numShots; i++) {
    window.setTimeout(
        function() {
          var x = Math.random() * svg.offsetWidth;
          var y = Math.random() * svg.offsetHeight;
          FF.StarShower(svg, x, y, numShards);
        },
        i * 500);
  }
};

FF.InitGame = function() {
  FF.SetState(FF.state);
};

FF.main = function() {
    FF.CELL_WIDTH = FF.MINIMAP_WIDTH / FF.W;
    FF.CELL_HEIGHT = FF.MINIMAP_HEIGHT / FF.H;

    FF.InitGame();
    FF.$("guess").focus();
};
