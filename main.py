from flask import Flask, render_template, request, send_file
import geopandas as gpd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def create_maps(nepal, dist1, selected_district, selected_gapa_napas):
        # Create district-level map
        fig1, ax1 = plt.subplots(figsize=(12, 10))
        ax1.set_xlabel('Longitude')
        ax1.set_ylabel('Latitude')
        ax1.set_title("Map of The Study Area", fontdict={"fontsize": '25', 'fontweight': '3'})
        dist1.plot(color="white", edgecolor="black", ax=ax1)
        if selected_district:
            com_id11 = dist1[dist1["dist_name"] == selected_district]
            com_id11.plot(column="dist_name", edgecolor="black", ax=ax1, legend=True)
        plt.tight_layout()
        buffer1 = io.BytesIO()
        plt.savefig(buffer1, format='png', dpi=300, bbox_inches='tight')
        buffer1.seek(0)
        district_map = base64.b64encode(buffer1.getvalue()).decode()
        plt.close(fig1)

        # Create GaPa_NaPa-level map
        fig2, ax2 = plt.subplots(figsize=(12, 10))
        ax2.set_xlabel('Longitude')
        ax2.set_ylabel('Latitude')
        ax2.set_title(f"Map of the study area in {selected_district}", fontdict={"fontsize": '25', 'fontweight': '3'})
        if selected_district:
            com_ids = nepal[nepal.DISTRICT == selected_district.upper()]
            com_ids.plot(color="white", edgecolor="black", ax=ax2)
            if selected_gapa_napas:
                com_id1 = com_ids[com_ids['GaPa_NaPa'].isin(selected_gapa_napas)]
                com_id1.plot(column="GaPa_NaPa", ax=ax2, legend=True)
        plt.tight_layout()
        buffer2 = io.BytesIO()
        plt.savefig(buffer2, format='png', dpi=300, bbox_inches='tight')
        buffer2.seek(0)
        gapa_napa_map = base64.b64encode(buffer2.getvalue()).decode()
        plt.close(fig2)

        return district_map, gapa_napa_map, buffer1, buffer2

@app.route('/', methods=['GET', 'POST'])
def index():
        nepal = gpd.read_file("data/local_unit.shp")
        dist1 = gpd.read_file("data/shape_files_of_districts_in_nepal.shp")
        districts = sorted(dist1.dist_name.unique())
        selected_district = request.form.get('district', '')
        gapa_napas = []
        selected_gapa_napas = []
        if selected_district:
            gapa_napas = sorted(nepal[nepal.DISTRICT == selected_district.upper()].GaPa_NaPa.unique())
            selected_gapa_napas = request.form.getlist('gapa_napa')

        district_map, gapa_napa_map, district_buffer, gapa_napa_buffer = create_maps(nepal, dist1, selected_district, selected_gapa_napas)

        return render_template('index.html', 
                               district_map=district_map,
                               gapa_napa_map=gapa_napa_map,
                               districts=districts,
                               selected_district=selected_district,
                               gapa_napas=gapa_napas,
                               selected_gapa_napas=selected_gapa_napas)

@app.route('/download_district_map')
def download_district_map():
        nepal = gpd.read_file("data/local_unit.shp")
        dist1 = gpd.read_file("data/shape_files_of_districts_in_nepal.shp")
        selected_district = request.args.get('district', '')
        _, _, buffer, _ = create_maps(nepal, dist1, selected_district, [])
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='district_map.png', mimetype='image/png')

@app.route('/download_gapa_napa_map')
def download_gapa_napa_map():
        nepal = gpd.read_file("data/local_unit.shp")
        dist1 = gpd.read_file("data/shape_files_of_districts_in_nepal.shp")
        selected_district = request.args.get('district', '')
        selected_gapa_napas = request.args.getlist('gapa_napa')
        _, _, _, buffer = create_maps(nepal, dist1, selected_district, selected_gapa_napas)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='gapa_napa_map.png', mimetype='image/png')

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)