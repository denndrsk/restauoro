import os

def create_renderer_html(project_folder, model1_path, model2_path):
    # Definiere den Pfad zur HTML-Datei im Projektordner
    renderer_output_path = os.path.join(project_folder, "render.html")

    # HTML-Inhalt, um die 3D-Szene darzustellen
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>STL Modelle mit Three.js</title>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <!-- Three.js und STLLoader sowie OrbitControls lokal einbinden -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/STLLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/OrbitControls.js"></script>

        <script>
            var scene = new THREE.Scene();
            var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            var renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            var loader = new THREE.STLLoader();

            // Farben beibehalten
            var material1 = new THREE.MeshStandardMaterial({{ color: 0xD3D3D3, roughness: 0.5, metalness: 0.1 }});
            var material2 = new THREE.MeshStandardMaterial({{ color: 0xF7A7B6, roughness: 0.5, metalness: 0.1 }});

            // Modell 1 laden und darstellen
            loader.load('{model1_path}', function (geometry) {{
                var mesh1 = new THREE.Mesh(geometry, material1);
                scene.add(mesh1);
                mesh1.position.x = 0;
            }});

            // Modell 2 laden und darstellen
            loader.load('{model2_path}', function (geometry) {{
                var mesh2 = new THREE.Mesh(geometry, material2);
                scene.add(mesh2);
                mesh2.position.x = 0;
            }});

            // Boden hinzufügen
            var planeGeometry = new THREE.PlaneGeometry(50, 50); // Größe des Bodens
            var planeMaterial = new THREE.MeshStandardMaterial({{ color: 0x808080, roughness: 0.8 }});
            var plane = new THREE.Mesh(planeGeometry, planeMaterial);
            plane.position.z = -0.1; // Leicht unterhalb des Modells in der z-Achse
            scene.add(plane);

            // Gitter hinzufügen
            var gridHelper = new THREE.GridHelper(50, 50); // Größe und Anzahl der Linien
            gridHelper.rotation.x = Math.PI / 2; // Drehe das Gitter in die x/y-Ebene
            scene.add(gridHelper);

            // Achsen-Helper hinzufügen
            var axesHelper = new THREE.AxesHelper(5); // Größe der Achsen (z.B. 5 Einheiten)
            scene.add(axesHelper);

            // Beleuchtung hinzufügen
            var ambientLight = new THREE.AmbientLight(0x404040, 1);  // Umgebungslicht
            scene.add(ambientLight);

            var pointLight1 = new THREE.PointLight(0xffffff, 1, 100);
            pointLight1.position.set(10, 10, 10);
            scene.add(pointLight1);

            var pointLight2 = new THREE.PointLight(0xffffff, 1, 100);
            pointLight2.position.set(-10, -10, 10);
            scene.add(pointLight2);

            var pointLight3 = new THREE.PointLight(0xffffff, 1, 100);
            pointLight3.position.set(10, -10, -10);
            scene.add(pointLight3);

            var pointLight4 = new THREE.PointLight(0xffffff, 1, 100);
            pointLight4.position.set(-10, 10, -10);
            scene.add(pointLight4);

            camera.position.set(-3.5, 0, 1.7);
            camera.up.set(0, 0, 1)
            camera.lookAt(0, 0, 1.7);
           
            // Aktivieren der OrbitControls für manuelles Drehen und Zoomen
            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.screenSpacePanning = false;

            function animate() {{
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
                controls.update();
            }}

            animate();

            window.addEventListener('resize', function () {{
                renderer.setSize(window.innerWidth, window.innerHeight);
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
            }});
        </script>
    </body>
    </html>
    """

    # Erstelle die HTML-Datei im Projektordner
    with open(renderer_output_path, 'w') as file:
        file.write(html_content)

    print(f"Die 3D-Szene wurde erfolgreich unter '{renderer_output_path}' gespeichert. Öffne die Datei im Browser.")
